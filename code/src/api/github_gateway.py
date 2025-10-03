import os
from datetime import datetime
from typing import Any, Dict, List
from .http_client import HTTPClient

def _load_query(name: str) -> str:
    """Carrega um arquivo de query GraphQL."""
    path = os.path.join("queries", name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class GitHubGateway:
    def __init__(self, client: HTTPClient):
        self.client = client
        self.search_repositories_query = _load_query("search_repositories.graphql")
        self.get_pr_count_query = _load_query("get_pr_count.graphql")
        self.get_pull_requests_query = _load_query("get_pull_requests.graphql")

    def search_top_repo_candidates(self, search_query: str, limit: int) -> List[Dict[str, Any]]:
        """Busca uma lista de candidatos a repositórios, retornando apenas dados básicos."""
        repos = []
        cursor = None
        
        while len(repos) < limit:
            page_size = min(100, limit - len(repos))
            variables = {"q": search_query, "first": page_size, "after": cursor}
            payload = {"query": self.search_repositories_query, "variables": variables}
            
            response = self.client.post(payload)
            data = response.get("data", {}).get("search", {})
            
            if not data or not data.get("nodes"): break

            for node in data["nodes"]:
                if node:
                    repos.append({
                        "owner": node["owner"]["login"], "name": node["name"],
                        "full_name": f"{node['owner']['login']}/{node['name']}",
                        "stargazers": node["stargazerCount"],
                    })
            
            if not data.get("pageInfo", {}).get("hasNextPage"): break
            cursor = data.get("pageInfo", {}).get("endCursor")

        return repos

    def get_repo_pr_count(self, owner: str, name: str) -> int:
        """Busca de forma confiável a contagem de PRs para um único repositório."""
        variables = {"owner": owner, "name": name}
        payload = {"query": self.get_pr_count_query, "variables": variables}
        response = self.client.post(payload)
        
        try:
            count = response["data"]["repository"]["pullRequests"]["totalCount"]
            return count
        except (KeyError, TypeError):
            return 0

    def get_pull_requests(self, owner: str, name: str, limit: int) -> List[Dict[str, Any]]:
        """Coleta pull requests de um repositório específico."""
        prs = []
        cursor = None
        while len(prs) < limit:
            page_size = min(100, limit - len(prs))
            variables = {"owner": owner, "name": name, "first": page_size, "after": cursor, "states": ["MERGED", "CLOSED"]}
            payload = {"query": self.get_pull_requests_query, "variables": variables}
            response = self.client.post(payload)
            data = response.get("data", {}).get("repository", {}).get("pullRequests", {})
            if not data or "nodes" not in data: break
            for pr_node in data.get("nodes", []):
                if not pr_node or not pr_node.get("createdAt") or not pr_node.get("closedAt"): continue
                created_at = datetime.fromisoformat(pr_node["createdAt"].replace("Z", "+00:00"))
                closed_at = datetime.fromisoformat(pr_node["closedAt"].replace("Z", "+00:00"))
                duration = (closed_at - created_at).total_seconds() / 3600
                prs.append({
                    "number": pr_node["number"], "title": pr_node["title"],
                    "author": pr_node.get("author", {}).get("login", "ghost") if pr_node.get("author") else "ghost",
                    "created_at": created_at.isoformat(), "closed_at": closed_at.isoformat(),
                    "merged": pr_node["merged"], "additions": pr_node["additions"], "deletions": pr_node["deletions"],
                    "changed_files": pr_node["changedFiles"], "description_length": len(pr_node.get("bodyText", "")),
                    "participants_count": pr_node.get("participants", {}).get("totalCount", 0),
                    "comments_count": pr_node.get("comments", {}).get("totalCount", 0),
                    "reviews_count": pr_node.get("reviews", {}).get("totalCount", 0),
                    "review_duration_hours": round(duration, 2), "url": pr_node["url"]
                })
            if not data.get("pageInfo", {}).get("hasNextPage"): break
            cursor = data.get("pageInfo", {}).get("endCursor")
        return prs[:limit]

