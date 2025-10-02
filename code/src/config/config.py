import os
from pathlib import Path
from dotenv import load_dotenv

# Encontra o diretório raiz do projeto para localizar o .env
# Path(__file__) -> config.py
# .parent -> Sprint/
# .parent -> src/
# .parent -> raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Carrega o token e valida sua existência
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Token do GitHub não encontrado. Verifique seu arquivo .env na raiz do projeto.")

# Constantes da API
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}