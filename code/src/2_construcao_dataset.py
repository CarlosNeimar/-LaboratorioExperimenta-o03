import os
import time
import csv
from datetime import datetime, timedelta, timezone
from github import Github, Auth, RateLimitExceededException, GithubException
from dotenv import load_dotenv

load_dotenv('./config/.env')

# --- CONFIGURAÇÕES ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOS_FILE = "eligible_repos.txt"
OUTPUT_CSV = "dataset_bruto.csv"
PROGRESS_FILE = "progress.txt"
RATE_LIMIT_THRESHOLD = 50
PR_TIME_LIMIT_DAYS = 730 # Aproximadamente 2 anos
MAX_PRS_PER_REPO = 100

class RateLimiter:
    """
    Classe para gerenciar de forma adaptativa os limites de taxa da API do GitHub.
    """
    def __init__(self, github_instance):
        self.github = github_instance

    def esperar_progresso(self):
        """
        Verifica o limite de taxa restante e aguarda se estiver abaixo do limiar de segurança.
        """
        try:
            core_rate_limit = self.github.get_rate_limit().resources.core
            remaining = core_rate_limit.remaining
            
            if remaining < RATE_LIMIT_THRESHOLD:
                reset_timestamp = core_rate_limit.reset.timestamp()
                sleep_time = max(0, reset_timestamp - time.time())
                print(f"Alerta de Limite de Taxa: {remaining} requisições restantes. Aguardando proativamente por {sleep_time:.2f} segundos para o reset.")
                time.sleep(sleep_time + 10)
        except Exception as e:
            print(f"Erro ao verificar o limite de taxa: {e}")
            time.sleep(60)

    def controlar_rate_limit(self):
        """
        Lida com a exceção RateLimitExceededException, aguardando o tempo necessário.
        """
        try:
            core_rate_limit = self.github.get_rate_limit().resources.core
            reset_timestamp = core_rate_limit.reset.timestamp()
            sleep_time = max(0, reset_timestamp - time.time())
            print(f"Limite de taxa da API excedido. Aguardando por {sleep_time:.2f} segundos.")
            time.sleep(sleep_time + 10)
        except Exception as e:
            print(f"Erro ao lidar com a exceção de limite de taxa: {e}")
            time.sleep(300)

def repos_processados():
    """
    Lê o arquivo de progresso para obter a lista de repositórios já processados.
    """
    if not os.path.exists(PROGRESS_FILE):
        return set()
    with open(PROGRESS_FILE, 'r') as f:
        return set(line.strip() for line in f)

def atualizar_repos_processados(repo_full_name):
    """
    Adiciona um repositório ao arquivo de progresso.
    """
    with open(PROGRESS_FILE, 'a') as f:
        f.write(f"{repo_full_name}\n")

def extrair_detalhes_pr(pr):
    """
    Extrai os detalhes necessários de um objeto PullRequest.
    """
    try:
        participants_count = len(set(p.login for p in pr.get_participants()))
    except Exception:
        participants_count = 1

    description_length = len(pr.body) if pr.body else 0

    return {
        "repo_full_name": pr.base.repo.full_name,
        "pr_number": pr.number,
        "title": pr.title,
        "author": pr.user.login if pr.user else "N/A",
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
        "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
        "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
        "state": pr.state,
        "description_length": description_length,
        "additions": pr.additions,
        "deletions": pr.deletions,
        "changed_files": pr.changed_files,
        "comments_count": pr.comments,
        "review_comments_count": pr.review_comments,
        "participants_count": participants_count,
        "url": pr.html_url
    }

def buscar_todos_prs():
    """
    Busca todos os pull requests dos repositórios listados e salva em um arquivo CSV bruto.
    """
    if not GITHUB_TOKEN:
        print("Erro: O token do GitHub não foi encontrado.")
        return

    try:
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        _ = g.get_user().login
    except Exception as e:
        print(f"Erro ao autenticar com o token do GitHub: {e}")
        return

    limiter = RateLimiter(g)

    try:
        with open(REPOS_FILE, 'r') as f:
            repos_to_process = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Erro: Arquivo de repositórios '{REPOS_FILE}' não encontrado. Execute o script 01 primeiro.")
        return

    repos = repos_processados()
    
    csv_headers = [
        "repo_full_name", "pr_number", "title", "author", "created_at", 
        "closed_at", "merged_at", "state", "description_length", "additions", "deletions", 
        "changed_files", "comments_count", "review_comments_count", 
        "participants_count", "url"
    ]

    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers, delimiter=';')
        if not file_exists:
            writer.writeheader()

        time_limit = datetime.now(timezone.utc) - timedelta(days=PR_TIME_LIMIT_DAYS)

        for repo_full_name in repos_to_process:
            if repo_full_name in repos:
                print(f"Repositório {repo_full_name} já processado. Pulando.")
                continue

            print(f"\n--- Processando repositório: {repo_full_name} ---")
            
            try:
                limiter.esperar_progresso()
                repo = g.get_repo(repo_full_name)
                pull_requests = repo.get_pulls(state='all', sort='created', direction='desc')
                pr_count = 0
                total_prs = pull_requests.totalCount
                print(f"Encontrados {total_prs} pull requests para {repo_full_name}.")

                for pr in pull_requests:
                    if pr.created_at < time_limit:
                        print(f"\n  - Atingido o limite de data ({PR_TIME_LIMIT_DAYS} dias). Parando a extração para {repo_full_name}.")
                        break
                    elif pr_count >= MAX_PRS_PER_REPO:
                        print(f"\n  - Atingido o limite máximo de PRs por repositório ({MAX_PRS_PER_REPO}). Parando a extração para {repo_full_name}.")
                        break

                    pr_count += 1
                    print(f"  - Extraindo PR {pr_count}/{total_prs} (#{pr.number})", end='\r')
                    
                    try:
                        limiter.esperar_progresso()
                        details = extrair_detalhes_pr(pr)
                        writer.writerow(details)

                    except RateLimitExceededException:
                        limiter.controlar_rate_limit()
                        details = extrair_detalhes_pr(pr)
                        writer.writerow(details)
                    
                    except GithubException as ge:
                        print(f"\nErro do GitHub ao processar PR #{pr.number} em {repo_full_name}: {ge.status} {ge.data}")
                        continue
                    
                    except Exception as e:
                        print(f"\nErro inesperado ao processar PR #{pr.number} em {repo_full_name}: {e}")
                        continue
                
                print(f"\nExtração para {repo_full_name} concluída.")
                atualizar_repos_processados(repo_full_name)

            except RateLimitExceededException:
                print(f"Limite de taxa atingido ao iniciar o processamento de {repo_full_name}. Tentando novamente após a espera...")
                limiter.controlar_rate_limit()
                print("O script irá parar. Por favor, execute-o novamente para continuar do ponto de parada.")
                break
            
            except GithubException as ge:
                print(f"Erro do GitHub ao acessar o repositório {repo_full_name}: {ge.status} {ge.data}. Pulando.")
                atualizar_repos_processados(repo_full_name)
                continue
            
            except Exception as e:
                print(f"Erro inesperado ao processar o repositório {repo_full_name}: {e}. Pulando.")
                atualizar_repos_processados(repo_full_name)
                continue

    print("\nProcesso de extração de dados brutos concluído.")

if __name__ == "__main__":
    buscar_todos_prs()