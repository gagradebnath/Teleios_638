mkdir config
mkdir backend\gateway
mkdir backend\adapters
mkdir backend\agents
mkdir backend\tools
mkdir backend\services
mkdir backend\db\migrations
mkdir frontend\public
mkdir frontend\src\api
mkdir frontend\src\components
mkdir tests\fixtures
mkdir tests\unit
mkdir tests\integration

type nul > .env.example
type nul > README.md
type nul > pytest.ini
type nul > docker-compose.yml

type nul > config\app.json
type nul > config\agents.json
type nul > config\models.json
type nul > config\prediction.json
type nul > config\tools.json

type nul > backend\Dockerfile
type nul > backend\requirements.txt
type nul > backend\main.py
type nul > backend\gateway\__init__.py
type nul > backend\gateway\middleware.py
type nul > backend\gateway\router.py
type nul > backend\gateway\schemas.py
type nul > backend\adapters\__init__.py
type nul > backend\adapters\anthropic_adapter.py
type nul > backend\adapters\model_adapter.py
type nul > backend\adapters\ollama_adapter.py
type nul > backend\adapters\openai_adapter.py
type nul > backend\adapters\vllm_adapter.py
type nul > backend\agents\__init__.py
type nul > backend\agents\base_agent.py
type nul > backend\agents\document_agent.py
type nul > backend\agents\execution_agent.py
type nul > backend\agents\explanation_agent.py
type nul > backend\agents\orchestrator.py
type nul > backend\agents\prediction_agent.py
type nul > backend\agents\qa_agent.py
type nul > backend\agents\retrieval_agent.py
type nul > backend\tools\__init__.py
type nul > backend\tools\base_tool.py
type nul > backend\tools\document_retrieval.py
type nul > backend\tools\python_exec.py
type nul > backend\tools\registry.py
type nul > backend\tools\sql_query.py
type nul > backend\tools\stats_analysis.py
type nul > backend\tools\vector_search.py
type nul > backend\services\__init__.py
type nul > backend\services\ocr_service.py
type nul > backend\services\sandbox_service.py
type nul > backend\services\sql_store.py
type nul > backend\services\vector_store.py
type nul > backend\db\__init__.py
type nul > backend\db\models.py
type nul > backend\db\session.py
type nul > backend\db\migrations\001_initial.sql

type nul > frontend\Dockerfile
type nul > frontend\package.json
type nul > frontend\public\index.html
type nul > frontend\src\App.jsx
type nul > frontend\src\api\gateway.js
type nul > frontend\src\components\ChatPanel.jsx
type nul > frontend\src\components\ExecutionPanel.jsx
type nul > frontend\src\components\IngestPanel.jsx
type nul > frontend\src\components\PDFViewer.jsx
type nul > frontend\src\components\PredictionPanel.jsx
type nul > frontend\src\components\StudyLayout.jsx
type nul > frontend\src\components\TabBar.jsx

type nul > tests\conftest.py
type nul > tests\pytest.ini
type nul > tests\fixtures\create_fixtures.py
type nul > tests\fixtures\sample.pdf
type nul > tests\unit\test_adapters.py
type nul > tests\unit\test_agents.py
type nul > tests\unit\test_tools.py
type nul > tests\integration\test_ingest.py
type nul > tests\integration\test_sandbox.py