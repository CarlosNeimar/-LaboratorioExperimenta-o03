import csv
import os
from api.github_gateway import GitHubGateway
from api.http_client import HTTPClient
from config import config

MIN_STARS = 1000
CANDIDATE_POOL_SIZE = 1000 
MIN_PULL_REQUESTS = 100
FINAL_REPOS_LIMIT = 200
PRS_PER_REPO_LIMIT = 200
OUTPUT_FILE = "pull_requests_raw.csv"

def main():
    if os.path.exists(OUTPUT_FILE):
        print(f"O arquivo '{OUTPUT_FILE}' já existe. Remova-o para uma nova coleta.")
        return

    client = HTTPClient(token=config.GITHUB_TOKEN)
    gateway = GitHubGateway(client=client)

    search_query = f"stars:>{MIN_STARS} sort:stars-desc"
    print(f"FASE 1: Buscando os {CANDIDATE_POOL_SIZE} repositórios mais populares (limite da API)...")
    
    candidate_repos = gateway.search_top_repo_candidates(
        search_query=search_query,
        limit=CANDIDATE_POOL_SIZE
    )
    if not candidate_repos:
        print("Busca inicial de candidatos falhou.")
        return
    print(f"Encontrados {len(candidate_repos)} candidatos.")

    print(f"\nFASE 2: Verificando cada candidato para encontrar {FINAL_REPOS_LIMIT} repositórios com >{MIN_PULL_REQUESTS} PRs...")
    final_repos = []
    for i, repo in enumerate(candidate_repos):
        print(f"  Verificando [{i+1}/{len(candidate_repos)}]: {repo['full_name']}...", end=" ")
        
        pr_count = gateway.get_repo_pr_count(owner=repo["owner"], name=repo["name"])
        print(f"PRs: {pr_count}")
        
        if pr_count > MIN_PULL_REQUESTS:
            repo['pull_requests_count'] = pr_count
            final_repos.append(repo)

        if len(final_repos) >= FINAL_REPOS_LIMIT:
            print(f"\nMeta de {FINAL_REPOS_LIMIT} repositórios qualificados atingida.")
            break

    if not final_repos:
        print("Nenhum repositório qualificado encontrado. Tente diminuir MIN_STARS.")
        return
    
    print(f"\nSeleção final: {len(final_repos)} repositórios. Iniciando coleta de pull requests...")
    all_prs = []
    for i, repo in enumerate(final_repos):
        print(f"[{i+1}/{len(final_repos)}] Coletando PRs de {repo['full_name']}...")
        prs = gateway.get_pull_requests(owner=repo["owner"], name=repo["name"], limit=PRS_PER_REPO_LIMIT)
        for pr in prs:
            pr["repo_full_name"] = repo["full_name"]
            pr["repo_stargazers"] = repo["stargazers"]
        all_prs.extend(prs)
        print(f"Coletados {len(prs)} PRs.")

    if not all_prs:
        print("Nenhum pull request foi coletado.")
        return

    print(f"\nSalvando {len(all_prs)} pull requests em '{OUTPUT_FILE}'...")
    fieldnames = [
        "repo_full_name", "repo_stargazers", "number", "title", "author",
        "created_at", "closed_at", "merged", "additions", "deletions",
        "changed_files", "description_length", "participants_count",
        "comments_count", "reviews_count", "review_duration_hours", "url"
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_prs)
    print("Coleta de dados concluída com sucesso!")

if __name__ == "__main__":
    main()

