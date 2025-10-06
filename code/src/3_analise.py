# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import csv
# --- CONFIGURAÇÕES ---
INPUT_CSV = "dataset_bruto.csv"
OUTPUT_CSV = "dataset_final.csv"
MIN_REVIEW_DURATION_HOURS = 1.0

def process_raw_data():
    """
    Carrega o dataset bruto, aplica filtros, calcula métricas e salva o dataset final.
    """
    print(f"Iniciando o processamento do arquivo de dados brutos: '{INPUT_CSV}'")

    try:
        df = pd.read_csv(INPUT_CSV, sep=';', on_bad_lines='warn')
        print(f"Carregadas {len(df)} linhas do dataset bruto.")
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{INPUT_CSV}' não encontrado. Execute o script 02 primeiro.")
        return

    # --- LIMPEZA E TRANSFORMAÇÃO DE DADOS ---
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['closed_at'] = pd.to_datetime(df['closed_at'], errors='coerce')
    df['merged_at'] = pd.to_datetime(df['merged_at'], errors='coerce')
    df.dropna(subset=['created_at', 'closed_at'], inplace=True)
    print(f"Linhas restantes após remover datas inválidas: {len(df)}")

    # --- APLICAÇÃO DOS FILTROS DO PROJETO ---
    # 1. Filtro de status: Apenas PRs com status 'MERGED' ou 'CLOSED'
    df_filtered = df[df['state'] == 'closed'].copy()
    print(f"Linhas restantes após filtrar por status 'closed': {len(df_filtered)}")
    # 2. Filtro de revisão: Deve possuir pelo menos uma revisão.
    df_filtered = df_filtered[df_filtered['review_comments_count'] > 0].copy()
    print(f"Linhas restantes após filtrar por mínimo de 1 comentário de revisão: {len(df_filtered)}")
    # 3. Filtro de duração da revisão: A diferença entre criação e fechamento deve ser > 1 hora.
    df_filtered['review_duration_hours'] = (df_filtered['closed_at'] - df_filtered['created_at']) / np.timedelta64(1, 'h')
    df_filtered = df_filtered[df_filtered['review_duration_hours'] > MIN_REVIEW_DURATION_HOURS].copy()
    print(f"Linhas restantes após filtrar por duração de revisão > {MIN_REVIEW_DURATION_HOURS} hora: {len(df_filtered)}")

    # --- CÁLCULO DE MÉTRICAS DERIVADAS ---
    df_filtered['merged'] = df_filtered['merged_at'].notna()
    df_filtered['comments_count'] = df_filtered['comments_count'].fillna(0) + df_filtered['review_comments_count'].fillna(0)
    df_filtered['comments_count'] = df_filtered['comments_count'].astype(int)
    df_filtered['review_duration_hours'] = df_filtered['review_duration_hours'].round(2)
    
    # --- ESTRUTURAÇÃO DO DATASET FINAL ---
    final_columns = [
        'repo_full_name', 'pr_number', 'title', 'author', 'created_at', 
        'closed_at', 'merged', 'additions', 'deletions', 'changed_files',
        'description_length', 'participants_count', 'comments_count', 
        'review_duration_hours', 'url'
    ]
    
    for col in final_columns:
        if col not in df_filtered.columns:
            df_filtered[col] = 0

    df_final = df_filtered[final_columns]

    df_final = df_final.astype({
        'pr_number': int,
        'additions': int,
        'deletions': int,
        'changed_files': int,
        'description_length': int,
        'participants_count': int,
        'comments_count': int
    })
    
    df_final['created_at'] = df_final['created_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df_final['closed_at'] = df_final['closed_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    df_final.to_csv(OUTPUT_CSV, index=False, sep=';', quoting=csv.QUOTE_NONNUMERIC)
    
    print(f"\nProcessamento concluído. O dataset final com {len(df_final)} linhas foi salvo em '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    process_raw_data()