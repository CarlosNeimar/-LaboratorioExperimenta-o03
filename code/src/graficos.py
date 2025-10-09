import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, spearmanr
import os
import warnings

# Ignorar avisos que podem poluir a saída
warnings.filterwarnings("ignore", category=UserWarning)

# --- Configurações ---
DATASET_FILE = 'exemplo_dois.csv' # Usando o dataset escolhido
OUTPUT_DIR = 'graficos_analise_final'

# --- Configurações Visuais dos Gráficos ---
sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['figure.autolayout'] = True # Ajusta o layout para evitar cortes

# --- Funções de Plotagem ---

def plot_boxplot(data, x, y, title, xlabel, ylabel, filename):
    """Cria e salva um gráfico boxplot."""
    plt.figure()
    ax = sns.boxplot(x=x, y=y, data=data, showfliers=False)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xticklabels(['Rejeitado', 'Aceito'])
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Gráfico salvo: {filename}")

def plot_scatterplot(data, x, y, title, xlabel, ylabel, filename):
    """Cria e salva um gráfico de dispersão."""
    plt.figure()
    # Usa uma amostra para evitar sobrecarga visual e de processamento
    sample_data = data.sample(n=min(len(data), 5000), random_state=42)
    ax = sns.regplot(x=x, y=y, data=sample_data,
                     scatter_kws={'alpha': 0.4, 's': 30, 'edgecolor': 'none'},
                     line_kws={'color': 'red', 'linewidth': 2})
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Gráfico salvo: {filename}")

# --- Funções de Análise por RQ ---

def run_all_analyses(df):
    """Executa a análise para todas as 8 RQs, conforme o enunciado."""
    
    print("\n" + "="*80)
    print("INICIANDO ANÁLISE COMPLETA DAS 8 QUESTÕES DE PESQUISA")
    print("="*80)
    print("\nJustificativa dos Testes Estatísticos:")
    print("- RQs 01-04 (Comparação Aceito vs. Rejeitado): Usamos o Teste de Mann-Whitney U, ideal para comparar duas amostras independentes (aceitos vs. rejeitados) sem assumir uma distribuição normal dos dados.")
    print("- RQs 05-08 (Correlações): Usamos a Correlação de Spearman, que mede a força e a direção da associação entre duas variáveis sem assumir uma relação linear, sendo mais robusta a outliers.")
    print("\nNota: Para as RQs 05-08, 'Número de Revisões' será representado pela métrica 'Número de Comentários' (comments_count), conforme justificado pela falta de uma coluna dedicada e pela forte relação conceitual entre as duas.")
    
    # --- DIMENSÃO A: FEEDBACK FINAL (STATUS DO PR) ---
    print("\n\n" + "-"*30 + " DIMENSÃO A: FEEDBACK FINAL " + "-"*30)
    
    # RQ01: Tamanho vs. Feedback
    print_header("RQ01: Relação entre o TAMANHO dos PRs e o FEEDBACK FINAL")
    for metrica, nome_metrica, arq in [('tamanho_total_linhas', 'Total de Linhas Alteradas', 'A_RQ01a_linhas_vs_feedback.png'), 
                                       ('changed_files', 'Arquivos Alterados', 'A_RQ01b_arquivos_vs_feedback.png')]:
        analyze_group_difference(df, metrica, nome_metrica)
        plot_boxplot(df, 'merged', metrica, f'Feedback Final vs. {nome_metrica}', 'Status do Pull Request', nome_metrica, arq)

    # RQ02: Tempo de Análise vs. Feedback
    print_header("RQ02: Relação entre o TEMPO DE ANÁLISE e o FEEDBACK FINAL")
    analyze_group_difference(df, 'review_duration_hours', 'Tempo de Análise (Horas)')
    plot_boxplot(df, 'merged', 'review_duration_hours', 'Feedback Final vs. Tempo de Análise', 'Status do Pull Request', 'Tempo de Análise (Horas)', 'A_RQ02_tempo_vs_feedback.png')

    # RQ03: Descrição vs. Feedback
    print_header("RQ03: Relação entre a DESCRIÇÃO dos PRs e o FEEDBACK FINAL")
    analyze_group_difference(df, 'description_length', 'Tamanho da Descrição (Caracteres)')
    plot_boxplot(df, 'merged', 'description_length', 'Feedback Final vs. Tamanho da Descrição', 'Status do Pull Request', 'Tamanho da Descrição (Caracteres)', 'A_RQ03_descricao_vs_feedback.png')

    # RQ04: Interações vs. Feedback
    print_header("RQ04: Relação entre as INTERAÇÕES nos PRs e o FEEDBACK FINAL")
    for metrica, nome_metrica, arq in [('participants_count', 'Número de Participantes', 'A_RQ04a_participantes_vs_feedback.png'), 
                                       ('comments_count', 'Número de Comentários', 'A_RQ04b_comentarios_vs_feedback.png')]:
        analyze_group_difference(df, metrica, nome_metrica)
        plot_boxplot(df, 'merged', metrica, f'Feedback Final vs. {nome_metrica}', 'Status do Pull Request', nome_metrica, arq)
        
    # --- DIMENSÃO B: NÚMERO DE REVISÕES (Proxy: Comentários) ---
    print("\n\n" + "-"*25 + " DIMENSÃO B: NÚMERO DE REVISÕES " + "-"*26)
    
    # RQ05: Tamanho vs. Número de Revisões
    print_header("RQ05: Relação entre o TAMANHO dos PRs e o NÚMERO DE REVISÕES")
    for metrica, nome_metrica, arq in [('tamanho_total_linhas', 'Total de Linhas Alteradas', 'B_RQ05a_linhas_vs_revisoes.png'), 
                                       ('changed_files', 'Arquivos Alterados', 'B_RQ05b_arquivos_vs_revisoes.png')]:
        analyze_correlation(df, metrica, 'comments_count', nome_metrica, 'Número de Comentários')
        plot_scatterplot(df, metrica, 'comments_count', f'Número de Comentários vs. {nome_metrica}', nome_metrica, 'Número de Comentários', arq)

    # RQ06: Tempo de Análise vs. Número de Revisões
    print_header("RQ06: Relação entre o TEMPO DE ANÁLISE e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'review_duration_hours', 'comments_count', 'Tempo de Análise (Horas)', 'Número de Comentários')
    plot_scatterplot(df, 'review_duration_hours', 'comments_count', 'Número de Comentários vs. Tempo de Análise', 'Tempo de Análise (Horas)', 'Número de Comentários', 'B_RQ06_tempo_vs_revisoes.png')

    # RQ07: Descrição vs. Número de Revisões
    print_header("RQ07: Relação entre a DESCRIÇÃO dos PRs e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'description_length', 'comments_count', 'Tamanho da Descrição (Caracteres)', 'Número de Comentários')
    plot_scatterplot(df, 'description_length', 'comments_count', 'Número de Comentários vs. Tamanho da Descrição', 'Tamanho da Descrição (Caracteres)', 'Número de Comentários', 'B_RQ07_descricao_vs_revisoes.png')

    # RQ08: Interações (Participantes) vs. Número de Revisões
    print_header("RQ08: Relação entre as INTERAÇÕES (Participantes) e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'participants_count', 'comments_count', 'Número de Participantes', 'Número de Comentários')
    plot_scatterplot(df, 'participants_count', 'comments_count', 'Número de Comentários vs. Número de Participantes', 'Número de Participantes', 'Número de Comentários', 'B_RQ08_participantes_vs_revisoes.png')

# --- Funções de Análise e Impressão ---

def print_header(title):
    print("\n" + "*"*len(title))
    print(title)
    print("*"*len(title))

def analyze_group_difference(df, metrica, nome_metrica):
    """Executa e imprime o resultado do teste de Mann-Whitney U."""
    print(f"\nAnalisando com a métrica: '{nome_metrica}'")
    print(f"H0: A mediana de '{nome_metrica}' é a mesma para PRs aceitos e rejeitados.")
    print(f"H1: A mediana de '{nome_metrica}' é diferente.")
    aceitos = df[df['merged'] == True][metrica]
    rejeitados = df[df['merged'] == False][metrica]
    stat, p_valor = mannwhitneyu(aceitos, rejeitados, alternative='two-sided')
    print(f"Resultado (Mann-Whitney U): p-valor = {p_valor:.5f}")
    if p_valor < 0.05:
        print("Conclusão: Rejeitamos H0. Existe uma diferença estatisticamente significativa.")
    else:
        print("Conclusão: Não rejeitamos H0. Não há evidência de diferença significativa.")

def analyze_correlation(df, var1, var2, nome_var1, nome_var2):
    """Executa e imprime o resultado da correlação de Spearman."""
    print(f"\nAnalisando a correlação entre '{nome_var1}' e '{nome_var2}'")
    print(f"H0: Não há correlação entre as variáveis.")
    print(f"H1: Existe correlação entre as variáveis.")
    corr, p_valor = spearmanr(df[var1], df[var2])
    print(f"Resultado (Spearman): Coeficiente (rho) = {corr:.4f}, p-valor = {p_valor:.5f}")
    if p_valor < 0.05:
        print(f"Conclusão: Rejeitamos H0. Existe uma correlação {'positiva' if corr > 0 else 'negativa'} fraca, mas estatisticamente significativa.")
    else:
        print("Conclusão: Não rejeitamos H0. Não há evidência de correlação.")

# --- Função Principal ---

def main():
    """Carrega os dados, prepara e executa todas as análises."""
    if not os.path.exists(DATASET_FILE):
        print(f"\nERRO: O arquivo '{DATASET_FILE}' não foi encontrado. Certifique-se de que ele está na mesma pasta que o script.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Carregando e preparando o dataset '{DATASET_FILE}'...")
    try:
        # quoting=1 é crucial para ler corretamente o CSV onde todos os campos estão entre aspas
        df = pd.read_csv(DATASET_FILE, sep=';', quoting=1)
        
        # Preparação das métricas conforme enunciado
        numeric_cols = ['additions', 'deletions', 'changed_files', 'description_length', 'participants_count', 'comments_count', 'review_duration_hours']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=numeric_cols + ['merged'], inplace=True)
        
        df['tamanho_total_linhas'] = df['additions'] + df['deletions']
        df['merged'] = df['merged'].apply(lambda x: x if isinstance(x, bool) else str(x).strip().upper() == 'TRUE')

        print(f"Dataset carregado com {len(df)} linhas válidas para análise.")
        
        run_all_analyses(df)
        
        print("\n\n" + "="*80)
        print(f"ANÁLISE CONCLUÍDA. Todos os gráficos foram salvos no diretório '{OUTPUT_DIR}'.")
        print("="*80)

    except Exception as e:
        print(f"\nOcorreu um erro crítico ao processar o arquivo: {e}")
        print("Verifique se o arquivo CSV não está corrompido e se o formato corresponde ao esperado.")

if __name__ == "__main__":
    main()
