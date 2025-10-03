from tqdm import tqdm
from .github_client import GitHubClient

def find_qualified_repos(client: GitHubClient, popular_repos: list):
    """Filtra repositórios para garantir que tenham pelo menos 100 PRs fechados."""
    qualified_repos = []
    for repo_name in tqdm(popular_repos, desc="Verificando repositórios"):
        count = client.get_closed_prs_count(repo_name)
        if count >= 100:
            qualified_repos.append(repo_name)
    return qualified_repos

def process_repo_prs(client: GitHubClient, repo_name: str):
    """Busca, filtra e formata os PRs de um único repositório."""
    valid_prs = []
    page = 1
    while True:
        pulls_data = client.get_pull_requests(repo_name, page)
        if not pulls_data:
            break

        for pr in pulls_data:
            reviews_url = pr.get('_links', {}).get('reviews', {}).get('href')
            if reviews_url and client.pr_has_reviews(reviews_url):
                valid_prs.append({
                    'repository': repo_name,
                    'pr_number': pr['number'],
                    'pr_title': pr['title'],
                    'state': 'MERGED' if pr.get('merged_at') else 'CLOSED',
                    'pr_url': pr['html_url'],
                    'created_at': pr['created_at'],
                    'closed_at': pr['closed_at'],
                    'merged_at': pr.get('merged_at'),
                })
        page += 1
    return valid_prs