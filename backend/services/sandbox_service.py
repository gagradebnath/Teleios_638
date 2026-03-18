"""
SandboxService — safe Python execution via RestrictedPython.
Allowed libraries: math, sympy, numpy, scipy, matplotlib.
All other imports are blocked. Execution is time-limited via ThreadPoolExecutor.
Stdout is captured. Matplotlib figures are returned as base64 PNGs.
"""
from __future__ import annotations
import base64
import io
import math
import sys
import concurrent.futures
from typing import Any

import structlog

logger = structlog.get_logger()

# Safe builtins — explicit allowlist, nothing else
_SAFE_BUILTINS = {
    "abs":       abs,
    "all":       all,
    "any":       any,
    "bool":      bool,
    "dict":      dict,
    "enumerate": enumerate,
    "float":     float,
    "int":       int,
    "len":       len,
    "list":      list,
    "map":       map,
    "max":       max,
    "min":       min,
    "print":     print,
    "range":     range,
    "round":     round,
    "set":       set,
    "sorted":    sorted,
    "str":       str,
    "sum":       sum,
    "tuple":     tuple,
    "type":      type,
    "zip":       zip,
    "True":      True,
    "False":     False,
    "None":      None,
}


class SandboxService:

    def __init__(self, config: dict):
        self.default_timeout = config.get("timeout_seconds", 10)

    def execute(self, code: str, timeout: int | None = None) -> dict[str, Any]:
        """
        Compile and execute code in a restricted environment.
        Returns:
          {"stdout": str, "figures": [base64_str], "error": None}   — on success
          {"stdout": "",  "figures": [],            "error": str}    — on failure/timeout
        """
        timeout = timeout or self.default_timeout

        try:
            from RestrictedPython import compile_restricted, safe_globals
            from RestrictedPython.Guards import (
                safe_builtins,
                guarded_iter_unpack_sequence,
            )
        except ImportError:
            return {
                "stdout":  "",
                "figures": [],
                "error":   "RestrictedPython is not installed.",
            }

        # Compile with RestrictedPython
        try:
            byte_code = compile_restricted(code, filename="<sandbox>", mode="exec")
        except SyntaxError as exc:
            return {"stdout": "", "figures": [], "error": f"SyntaxError: {exc}"}

        # Build restricted globals
        restricted_globals = dict(safe_globals)
        restricted_globals["__builtins__"] = dict(safe_builtins)
        restricted_globals["__builtins__"].update(_SAFE_BUILTINS)

        # Inject allowed scientific libraries
        try:
            import numpy as np
            restricted_globals["numpy"] = np
            restricted_globals["np"]    = np
        except ImportError:
            pass

        try:
            import sympy
            restricted_globals["sympy"] = sympy
            # Convenience: expose common sympy symbols at top level
            restricted_globals["symbols"] = sympy.symbols
            restricted_globals["diff"]    = sympy.diff
            restricted_globals["integrate"] = sympy.integrate
            restricted_globals["solve"]   = sympy.solve
            restricted_globals["Matrix"]  = sympy.Matrix
            restricted_globals["pi"]      = sympy.pi
            restricted_globals["E"]       = sympy.E
        except ImportError:
            pass

        try:
            import scipy
            restricted_globals["scipy"] = scipy
        except ImportError:
            pass

        restricted_globals["math"] = math

        # Set up matplotlib with non-interactive Agg backend
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            plt.close("all")   # clear any lingering figures
            restricted_globals["matplotlib"] = matplotlib
            restricted_globals["plt"]        = plt
        except ImportError:
            plt = None

        # ── Execute in a thread with timeout ────────────────────────────────
        stdout_capture = io.StringIO()
        restricted_globals["__builtins__"]["print"] = lambda *a, **kw: print(
            *a, **kw, file=stdout_capture
        )

        def _run():
            exec(byte_code, restricted_globals)  # noqa: S102

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_run)
            try:
                future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                return {
                    "stdout":  stdout_capture.getvalue(),
                    "figures": [],
                    "error":   f"Execution timed out after {timeout}s.",
                }
            except Exception as exc:
                return {
                    "stdout":  stdout_capture.getvalue(),
                    "figures": [],
                    "error":   str(exc),
                }

        # ── Capture matplotlib figures ───────────────────────────────────────
        figures: list[str] = []
        if plt is not None:
            for fig_num in plt.get_fignums():
                try:
                    fig = plt.figure(fig_num)
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
                    buf.seek(0)
                    figures.append(base64.b64encode(buf.read()).decode("utf-8"))
                    plt.close(fig)
                except Exception as exc:
                    logger.warning("sandbox.figure_capture_error", error=str(exc))

        return {
            "stdout":  stdout_capture.getvalue(),
            "figures": figures,
            "error":   None,
        }