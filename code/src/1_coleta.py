# -*- coding: utf-8 -*-
import os
import time
from github import Github, Auth, RateLimitExceededException
from dotenv import load_dotenv

load_dotenv('./config/.env')
# --- CONFIGURAÇÕES ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
NUM_REPOS = 200
MIN_PULL_REQUESTS = 100
OUTPUT_FILE = "repos_elegiveis.txt"
RATE_LIMIT_THRESHOLD = 50

def esperar_reset_limit(g):
    """
    Função auxiliar para aguardar o reset da janela de limite de taxa da API.
    É chamada quando uma RateLimitExceededException é capturada.
    """
    core_rate_limit = g.get_rate_limit().resources.core
    reset_timestamp = core_rate_limit.reset.timestamp()
    sleep_time = max(0, (reset_timestamp - time.time()))
    print(f"Limite de taxa da API atingido. Aguardando por {sleep_time:.2f} segundos.")
    time.sleep(sleep_time + 5)

def verificar_taxa_limit(g):
    """
    Verifica o limite de taxa e aguarda se estiver abaixo do previsto
    """
    core_rate_limit = g.get_rate_limit().resources.core
    if core_rate_limit.remaining < RATE_LIMIT_THRESHOLD:
        reset_timestamp = core_rate_limit.reset.timestamp()
        sleep_time = max(0, (reset_timestamp - time.time()))
        print(f"Limite de taxa próximo do fim ({core_rate_limit.remaining} restantes). Aguardando por {sleep_time:.2f} segundos.")
        time.sleep(sleep_time + 5)

def buscar_repositorios_populares():
    """
    Busca os repositórios mais populares no GitHub e os filtra com base no número mínimo de pull requests.
    """
    if not GITHUB_TOKEN:
        print("Erro: O token do GitHub não foi encontrado. Defina a variável de ambiente GITHUB_TOKEN.")
        return
    try:
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        _ = g.get_user().login
    except Exception as e:
        print(f"Erro ao autenticar com o token do GitHub: {e}")
        print("Verifique se o token é válido e possui as permissões necessárias.")
        return
    
    print(f"Iniciando a busca pelos {NUM_REPOS} repositórios mais populares...")
    repos_elegiveis = []

    try:
        repos = g.search_repositories(query='stars:>1', sort='stars', order='desc')
        
        repo_count = 0
        for repo in repos:
            if len(repos_elegiveis) >= NUM_REPOS:
                break

            repo_count += 1
            print(f"Verificando repositório #{repo_count}: {repo.full_name} (Estrelas: {repo.stargazers_count})")
            verificar_taxa_limit(g)

            try:
                pull_requests = repo.get_pulls(state='all') 
                if pull_requests.totalCount >= MIN_PULL_REQUESTS:
                    print(f"  -> Repositório {repo.full_name} é elegível com {pull_requests.totalCount} pull requests.")
                    repos_elegiveis.append(repo.full_name)
                else:
                    print(f"  -> Repositório {repo.full_name} ignorado. Possui apenas {pull_requests.totalCount} pull requests.")

            except RateLimitExceededException:
                esperar_reset_limit(g)
                pull_requests = repo.get_pulls(state='all')
                if pull_requests.totalCount >= MIN_PULL_REQUESTS:
                    print(f"  -> Repositório {repo.full_name} é elegível com {pull_requests.totalCount} pull requests (após espera).")
                    repos_elegiveis.append(repo.full_name)
                else:
                    print(f"  -> Repositório {repo.full_name} ignorado (após espera).")
            
            except Exception as e:
                print(f"  -> Ocorreu um erro ao verificar o repositório {repo.full_name}: {e}")
                continue

    except RateLimitExceededException:
        print("Limite de taxa da API atingido durante a busca inicial de repositórios.")
        esperar_reset_limit(g)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    if repos_elegiveis:
        with open(OUTPUT_FILE, 'w') as f:
            for nome_repo in repos_elegiveis:
                f.write(f"{nome_repo}\n")
        print(f"\nBusca concluída. {len(repos_elegiveis)} repositórios elegíveis foram salvos em '{OUTPUT_FILE}'.")
    else:
        print("\nNenhum repositório elegível foi encontrado com os critérios especificados.")

if __name__ == "__main__":
    buscar_repositorios_populares()