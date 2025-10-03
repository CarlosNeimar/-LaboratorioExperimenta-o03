import pandas as pd
import os

RAW_DATA_FILE = "pull_requests_raw.csv"
FINAL_DATASET_FILE = "dataset.csv"

def main():
    """
    Este script lê os dados brutos, realiza uma limpeza básica
    e salva o dataset final que será usado para análise.
    """
    if not os.path.exists(RAW_DATA_FILE):
        print(f"Arquivo de dados brutos '{RAW_DATA_FILE}' não encontrado.")
        return
        
    print(f"Lendo dados de '{RAW_DATA_FILE}'...")
    df = pd.read_csv(RAW_DATA_FILE)
    df = df[df["review_duration_hours"] >= 0]
    
    numeric_cols = [
        "repo_stargazers", "additions", "deletions", "changed_files",
        "description_length", "participants_count", "comments_count",
        "reviews_count", "review_duration_hours"
    ]
    df.dropna(subset=numeric_cols, inplace=True)

    print(f"O dataset final contém {len(df)} registros.")

    df.to_csv(FINAL_DATASET_FILE, index=False, encoding="utf-8")
    print(f"Dataset final salvo em '{FINAL_DATASET_FILE}'.")

if __name__ == "__main__":
    main()
