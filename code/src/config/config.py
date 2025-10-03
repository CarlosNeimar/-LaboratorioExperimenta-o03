import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Obtém o token do GitHub a partir das variáveis de ambiente
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Validação para garantir que o token foi definido
if not GITHUB_TOKEN:
    raise ValueError(
        "A variável de ambiente GITHUB_TOKEN não foi definida. "
        "Crie um arquivo .env na raiz do projeto e adicione a variável."
    )
