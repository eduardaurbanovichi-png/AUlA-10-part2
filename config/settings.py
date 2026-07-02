import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURAÇÃO DE CREDENCIAIS DIRETAS (Conforme seu link real do Neon)
# ==============================================================================
DATABASE_URL = "postgresql+psycopg://neondb_owner:npg_kHhtfQIgr3P2@ep-young-scene-atliduu0-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require"
UPLOAD_FOLDER = BASE_DIR / "assets" / "images"
SECRET_KEY = "chave_secreta_fixa_para_producao_e_ambiente_local"
# ==============================================================================

# Garantir infraestrutura física local de diretórios
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "logs" / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("CVPlatform")