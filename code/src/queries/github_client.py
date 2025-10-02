import time
import requests
from ...code.src.config import config  # Importa as configurações do mesmo módulo

class GitHubClient:
    """Um cliente para interagir com a API REST do GitHub."""

    def _make_request(self, url, params=None):
        """Método privado para fazer requisições, tratar rate limit e re-tentativas."""
        self._check_rate_limit()
        try:
            response = requests.get(url, headers=config.HEADERS, params=params)
            
            if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
                retry_after = int(response.headers.get('retry-after', 60))
                print(f"\nLimite de taxa da API de Busca excedido. Aguardando {retry_after} segundos para tentar novamente...")
                time.sleep(retry_after + 1) # Adiciona 1 segundo de margem
                
                response = requests.get(url, headers=config.HEADERS, params=params)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\nErro na requisição para {url}: {e}")
            return None
    def _check_rate_limit(self):
        """Verifica o limite de requisições e aguarda se estiver baixo."""
        try:
            response = requests.get(f"{config.GITHUB_API_URL}/rate_limit", headers=config.HEADERS)
            response.raise_for_status()
            data = response.json().get('resources', {}).get('core', {})
            if data.get('remaining', 100) < 50:
                reset_time = data.get('reset', time.time() + 60)
                wait_time = max(0, reset_time - time.time()) + 5
                print(f"\nLimite de taxa baixo ({data.get('remaining')} restantes). Aguardando {wait_time:.0f}s...")
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao verificar o limite de taxa: {e}. Aguardando 60s.")
            time.sleep(60)

    def get_popular_repos(self, count=200):
        """Busca os repositórios mais populares por estrelas."""
        repos = []
        pages = (count // 100) + (1 if count % 100 else 0)
        for page in range(1, pages + 1):
            params = {
                "q": "stars:>1000",
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": page,
            }
            data = self._make_request(f"{config.GITHUB_API_URL}/search/repositories", params=params)
            if data and 'items' in data:
                repos.extend(item['full_name'] for item in data['items'])
        return repos[:count]

    def get_closed_prs_count(self, repo_name):
        """Retorna a contagem de PRs fechados para um repositório."""
        params = {"q": f"is:pr is:closed repo:{repo_name}", "per_page": 1}
        data = self._make_request(f"{config.GITHUB_API_URL}/search/issues", params=params)
        return data.get('total_count', 0) if data else 0

    def get_pull_requests(self, repo_name, page):
        """Busca uma página de PRs fechados de um repositório."""
        params = {"state": "closed", "per_page": 100, "page": page}
        return self._make_request(f"{config.GITHUB_API_URL}/repos/{repo_name}/pulls", params=params)

    def pr_has_reviews(self, reviews_url):
        """Verifica se um PR tem pelo menos uma revisão."""
        data = self._make_request(reviews_url, params={"per_page": 1})
        return bool(data) # Retorna True se a lista não for vazia