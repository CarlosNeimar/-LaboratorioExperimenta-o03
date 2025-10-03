import requests
import time
from typing import Any, Dict

class HTTPClient:
    def __init__(self, token: str, endpoint: str = "https://api.github.com/graphql"):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"bearer {token}", "Accept": "application/json"})
        self.endpoint = endpoint

    def post(self, payload: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Envia uma requisição POST com lógica de retry para erros de servidor.
        """
        retries = 0
        while retries < max_retries:
            try:
                resp = self.session.post(self.endpoint, json=payload, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Erro na requisição HTTP: {e}. Tentativa {retries}/{max_retries}...")
                if retries >= max_retries:
                    print("Número máximo de tentativas atingido. Falha na requisição.")
                    return {} 
                time.sleep(2 ** (retries - 1))
        return {}
