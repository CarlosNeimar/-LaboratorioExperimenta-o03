from tqdm import tqdm
from .github_client import GitHubClient
from . import data_processor
from . import file_exporter

def run_analysis():
    """Função principal que orquestra todo o processo de análise."""
    print("Iniciando análise de Pull Requests do GitHub...")
    client = GitHubClient()

    # Etapa 1: Buscar os 200 repositórios mais populares
    print("\nBuscando os 200 repositórios mais populares...")
    popular_repos = client.get_popular_repos(count=200)
    print(f"Encontrados {len(popular_repos)} repositórios.")
    if not popular_repos: return

    # Etapa 2: Filtrar repositórios que atendem ao critério de 100 PRs
    print("\nFiltrando repositórios por número de Pull Requests (>= 100)...")
    qualified_repos = data_processor.find_qualified_repos(client, popular_repos)
    print(f"\n{len(qualified_repos)} repositórios qualificados.")
    if not qualified_repos: return

    # Etapa 3: Coletar e filtrar os PRs de cada repositório
    print("\nIniciando a coleta de Pull Requests com revisões. Isso pode demorar...")
    all_valid_prs = []
    for repo_name in tqdm(qualified_repos, desc="Coletando PRs"):
        repo_prs = data_processor.process_repo_prs(client, repo_name)
        all_valid_prs.extend(repo_prs)

    # Etapa 4: Exportar os dados para CSV
    print(f"\nColeta finalizada. Total de {len(all_valid_prs)} PRs encontrados.")
    file_exporter.save_to_csv(all_valid_prs, "github_pull_requests.csv")