import pandas as pd

def save_to_csv(data: list[dict], filename: str):
    """Salva uma lista de dicionários em um arquivo CSV."""
    if not data:
        print("Nenhum dado para exportar.")
        return

    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nDados exportados com sucesso para o arquivo '{filename}'!")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o arquivo CSV: {e}")