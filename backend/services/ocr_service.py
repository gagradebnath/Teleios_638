"""
OCRService — PDF ingestion and block extraction pipeline.
Uses PyMuPDF (fitz) for layout parsing.
Image OCR uses EasyOCR if configured, falling back to pytesseract.

Produces a flat list of typed block dicts per page:
  TextBlock    — {"type": "text",     "content": str,        "page": int, "bbox": [...]}
  EquationBlock— {"type": "equation", "image_b64": str,      "page": int, "description": str|None}
  FigureBlock  — {"type": "figure",   "image_b64": str,      "page": int, "description": str|None}
  TableBlock   — {"type": "table",    "rows": [[str]],       "page": int, "caption": None}
"""
from __future__ import annotations
import base64
import io
from typing import Any

import structlog

logger = structlog.get_logger()

# Equation vs figure heuristic: images smaller than this area (px²) → equation
_EQUATION_AREA_THRESHOLD = 40_000   # ~200×200 px


class OCRService:

    def __init__(self, config: dict):
        self.engine              = config.get("engine", "easyocr")
        self.equation_detection  = config.get("equation_detection", True)
        self.figure_extraction   = config.get("figure_extraction", True)
        self.table_extraction    = config.get("table_extraction", True)
        self._ocr_reader         = None   # lazy-loaded

    # ── Public API ────────────────────────────────────────────────────────────

    async def extract_blocks(self, pdf_bytes: bytes) -> list[dict[str, Any]]:
        """
        Main entry point. Accepts raw PDF bytes, returns a flat list of blocks.
        Async signature for compatibility with agent code; internally synchronous
        (PyMuPDF is not async-native).
        """
        import fitz  # PyMuPDF

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            logger.error("ocr.open_failed", error=str(exc))
            return []

        all_blocks: list[dict] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_idx = page_num + 1   # 1-based page numbers

            # 1. Text blocks
            all_blocks.extend(self._extract_text(page, page_idx))

            # 2. Images (figures + equations)
            if self.figure_extraction or self.equation_detection:
                all_blocks.extend(self._extract_images(doc, page, page_idx))

            # 3. Tables
            if self.table_extraction:
                all_blocks.extend(self._extract_tables(page, page_idx))

        doc.close()
        logger.info("ocr.done", pages=len(doc), blocks=len(all_blocks))
        return all_blocks

    # ── Text ──────────────────────────────────────────────────────────────────

    def _extract_text(self, page, page_idx: int) -> list[dict]:
        blocks = []
        raw = page.get_text("dict")
        for block in raw.get("blocks", []):
            if block.get("type") != 0:   # type 0 = text
                continue
            lines = block.get("lines", [])
            text  = " ".join(
                span["text"]
                for line in lines
                for span in line.get("spans", [])
            ).strip()
            if not text:
                continue
            bbox = block.get("bbox", [0, 0, 0, 0])
            blocks.append({
                "type":    "text",
                "content": text,
                "page":    page_idx,
                "bbox":    list(bbox),
            })
        return blocks

    # ── Images ────────────────────────────────────────────────────────────────

    def _extract_images(self, doc, page, page_idx: int) -> list[dict]:
        blocks = []
        image_list = page.get_images(full=True)

        for img_info in image_list:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            img_bytes  = base_image.get("image", b"")
            width      = base_image.get("width",  0)
            height     = base_image.get("height", 0)
            area       = width * height

            image_b64  = base64.b64encode(img_bytes).decode("utf-8")
            description = self._ocr_image(img_bytes)

            block_type = "equation" if area < _EQUATION_AREA_THRESHOLD else "figure"
            blocks.append({
                "type":        block_type,
                "image_b64":   image_b64,
                "page":        page_idx,
                "description": description,
            })

        return blocks

    # ── Tables ────────────────────────────────────────────────────────────────

    def _extract_tables(self, page, page_idx: int) -> list[dict]:
        blocks = []
        try:
            tables = page.find_tables()
        except AttributeError:
            # find_tables() requires PyMuPDF ≥ 1.23
            return blocks

        for table in tables:
            try:
                rows = table.extract()   # list[list[str|None]]
                # Clean None cells to empty string
                cleaned = [
                    [cell if cell is not None else "" for cell in row]
                    for row in rows
                ]
                if not cleaned:
                    continue
                blocks.append({
                    "type":    "table",
                    "rows":    cleaned,
                    "caption": None,
                    "page":    page_idx,
                })
            except Exception as exc:
                logger.warning("ocr.table_extract_error", page=page_idx, error=str(exc))

        return blocks

    # ── OCR helper ────────────────────────────────────────────────────────────

    def _ocr_image(self, img_bytes: bytes) -> str | None:
        """
        Run OCR on an image and return extracted text, or None on failure.
        Tries EasyOCR first (if configured), falls back to pytesseract.
        """
        if not img_bytes:
            return None

        # EasyOCR path
        if self.engine == "easyocr":
            try:
                reader = self._get_easyocr_reader()
                result = reader.readtext(img_bytes, detail=0)
                return " ".join(result).strip() or None
            except Exception as exc:
                logger.debug("ocr.easyocr_failed", error=str(exc))

        # pytesseract fallback
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(io.BytesIO(img_bytes))
            text  = pytesseract.image_to_string(image).strip()
            return text or None
        except Exception as exc:
            logger.debug("ocr.pytesseract_failed", error=str(exc))

        return None

    def _get_easyocr_reader(self):
        """Lazy-load EasyOCR reader (first call takes ~10s to load model)."""
        if self._ocr_reader is None:
            import easyocr
            self._ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        return self._ocr_reader