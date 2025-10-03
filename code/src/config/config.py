import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError(
        "A variável de ambiente GITHUB_TOKEN não foi definida. "
        "Crie um arquivo .env na raiz do projeto e adicione a variável."
    )

