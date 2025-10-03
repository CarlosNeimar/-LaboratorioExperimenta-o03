import pandas as pd
import os
from scipy.stats import spearmanr

DATASET_FILE = "dataset.csv"

def main():
    if not os.path.exists(DATASET_FILE):
        print(f"Arquivo de dataset '{DATASET_FILE}' não encontrado.")
        return

    print(f"Analisando o dataset '{DATASET_FILE}'...")
    df = pd.read_csv(DATASET_FILE)

    print("\n--- Métricas Descritivas (Mediana) ---")
    median_duration = df['review_duration_hours'].median()
    print(f"Mediana da Duração do Review (horas): {median_duration:.2f}")
    df['pr_size'] = df['additions'] + df['deletions']
    median_pr_size = df['pr_size'].median()
    print(f"Mediana do Tamanho do PR (linhas alteradas): {median_pr_size:.2f}")
    median_participants = df['participants_count'].median()
    print(f"Mediana de Participantes: {median_participants:.2f}")
    median_comments = df['comments_count'].median()
    print(f"Mediana de Comentários: {median_comments:.2f}")

    print("\n--- Análise de Correlação (Spearman) ---")
    corr_size_duration, p_size_duration = spearmanr(df['pr_size'], df['review_duration_hours'])
    print(f"Correlação entre Tamanho do PR e Duração do Review:")
    print(f"  - Coeficiente (rho): {corr_size_duration:.4f}")
    print(f"  - P-valor: {p_size_duration:.4f} {'(Estatisticamente significante)' if p_size_duration < 0.05 else '(Não significante)'}")
    
    corr_part_duration, p_part_duration = spearmanr(df['participants_count'], df['review_duration_hours'])
    print(f"\nCorrelação entre Participantes e Duração do Review:")
    print(f"  - Coeficiente (rho): {corr_part_duration:.4f}")
    print(f"  - P-valor: {p_part_duration:.4f} {'(Estatisticamente significante)' if p_part_duration < 0.05 else '(Não significante)'}")
    
    print("\nAnálise concluída.")

if __name__ == "__main__":
    main()
