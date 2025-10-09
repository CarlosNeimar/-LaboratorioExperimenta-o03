import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, spearmanr
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# --- Configurações ---
DATASET_FILE = 'exemplo_dois.csv'
OUTPUT_DIR = 'graficos_analise_final'

# --- Configurações Visuais dos Gráficos ---
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# --- Funções de Plotagem ---

def plot_boxplot(data, x, y, title, xlabel, ylabel, filename):
    """Cria e salva um gráfico boxplot, otimizado para clareza."""
    plt.figure()
    ax = sns.boxplot(x=x, y=y, data=data, showfliers=False, palette="viridis")
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xticklabels(['Rejeitado', 'Aceito'])
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Gráfico salvo: {filename}")

def plot_correlation_hexbin(data, x, y, title, xlabel, ylabel, filename):
    """
    Cria um gráfico de densidade hexagonal (hexbin) com escala logarítmica e uma barra de cores (legenda).
    Esta é a abordagem correta para visualizar a densidade de dados sobrepostos.
    """
    fig, ax = plt.subplots()
    
    x_log = data[x] + 1
    y_log = data[y] + 1
    
    hb = ax.hexbin(x_log, y_log, gridsize=50, cmap='viridis', mincnt=1, xscale='log', yscale='log')
    
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('Contagem de Pull Requests', fontsize=12)
    
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel(f"{xlabel} (Escala Log)", fontsize=14)
    ax.set_ylabel(f"{ylabel} (Escala Log)", fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close(fig)
    print(f"-> Gráfico de densidade (Hexbin) com legenda salvo: {filename}")

def run_all_analyses(df):
    print("\n" + "="*80)
    print("INICIANDO ANÁLISE COMPLETA DAS 8 QUESTÕES DE PESQUISA")
    print("="*80)
    
    print("\n" + "-"*35 + " JUSTIFICATIVA METODOLÓGICA " + "-"*34)
    print("Conforme solicitado, os seguintes testes estatísticos foram escolhidos:\n")
    print("1. Para RQs 01-04 (Comparação Aceito vs. Rejeitado):")
    print("   - Teste de Mann-Whitney U: Utilizado para comparar duas amostras independentes (PRs aceitos e rejeitados). Foi escolhido por ser um teste não-paramétrico, que não exige que os dados sigam uma distribuição normal, uma característica comum em métricas de software que são frequentemente assimétricas.\n")
    print("2. Para RQs 05-08 (Análise de Correlação):")
    print("   - Correlação de Spearman (rho): Foi escolhida em detrimento da correlação de Pearson. A justificativa é dupla:")
    print("     a) Não-linearidade: Spearman avalia a relação monotônica (se uma variável tende a aumentar quando a outra aumenta, por exemplo), não se restringindo a relações perfeitamente lineares, que são raras nestes dados.")
    print("     b) Robustez a Outliers: É muito menos sensível a valores extremos (outliers), que são prevalentes em métricas como 'linhas de código' ou 'número de comentários'. Isso fornece uma medida de correlação mais estável e confiável para o conjunto de dados.\n")
    print("Nota: 'Número de Revisões' será representado pela métrica 'Número de Comentários' (comments_count), pois é o indicador de interação de revisão mais direto disponível no dataset.")
    print("-" * 97)
    
    print("\n\n" + "-"*30 + " DIMENSÃO A: FEEDBACK FINAL " + "-"*30)
    print_header("RQ01: Relação entre o TAMANHO dos PRs e o FEEDBACK FINAL")
    for metrica, nome_metrica, arq in [('tamanho_total_linhas', 'Total de Linhas Alteradas', 'A_RQ01a_linhas_vs_feedback.png'), ('changed_files', 'Arquivos Alterados', 'A_RQ01b_arquivos_vs_feedback.png')]:
        analyze_group_difference(df, metrica, nome_metrica)
        plot_boxplot(df, 'merged', metrica, f'Feedback Final vs. {nome_metrica}', 'Status do Pull Request', nome_metrica, arq)
    print_header("RQ02: Relação entre o TEMPO DE ANÁLISE e o FEEDBACK FINAL")
    analyze_group_difference(df, 'review_duration_hours', 'Tempo de Análise (Horas)')
    plot_boxplot(df, 'merged', 'review_duration_hours', 'Feedback Final vs. Tempo de Análise', 'Status do Pull Request', 'Tempo de Análise (Horas)', 'A_RQ02_tempo_vs_feedback.png')
    print_header("RQ03: Relação entre a DESCRIÇÃO dos PRs e o FEEDBACK FINAL")
    analyze_group_difference(df, 'description_length', 'Tamanho da Descrição (Caracteres)')
    plot_boxplot(df, 'merged', 'description_length', 'Feedback Final vs. Tamanho da Descrição', 'Status do Pull Request', 'Tamanho da Descrição (Caracteres)', 'A_RQ03_descricao_vs_feedback.png')
    print_header("RQ04: Relação entre as INTERAÇÕES nos PRs e o FEEDBACK FINAL")
    for metrica, nome_metrica, arq in [('participants_count', 'Número de Participantes', 'A_RQ04a_participantes_vs_feedback.png'), ('comments_count', 'Número de Comentários', 'A_RQ04b_comentarios_vs_feedback.png')]:
        analyze_group_difference(df, metrica, nome_metrica)
        plot_boxplot(df, 'merged', metrica, f'Feedback Final vs. {nome_metrica}', 'Status do Pull Request', nome_metrica, arq)

    print("\n\n" + "-"*25 + " DIMENSÃO B: NÚMERO DE REVISÕES " + "-"*26)
    print_header("RQ05: Relação entre o TAMANHO dos PRs e o NÚMERO DE REVISÕES")
    for metrica, nome_metrica, arq in [('tamanho_total_linhas', 'Total de Linhas Alteradas', 'B_RQ05a_linhas_vs_revisoes.png'), ('changed_files', 'Arquivos Alterados', 'B_RQ05b_arquivos_vs_revisoes.png')]:
        analyze_correlation(df, metrica, 'comments_count', nome_metrica, 'Número de Comentários')
        plot_correlation_hexbin(df, metrica, 'comments_count', f'Número de Comentários vs. {nome_metrica}', nome_metrica, 'Número de Comentários', arq)
    print_header("RQ06: Relação entre o TEMPO DE ANÁLISE e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'review_duration_hours', 'comments_count', 'Tempo de Análise (Horas)', 'Número de Comentários')
    plot_correlation_hexbin(df, 'review_duration_hours', 'comments_count', 'Número de Comentários vs. Tempo de Análise', 'Tempo de Análise (Horas)', 'Número de Comentários', 'B_RQ06_tempo_vs_revisoes.png')
    print_header("RQ07: Relação entre a DESCRIÇÃO dos PRs e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'description_length', 'comments_count', 'Tamanho da Descrição (Caracteres)', 'Número de Comentários')
    plot_correlation_hexbin(df, 'description_length', 'comments_count', 'Número de Comentários vs. Tamanho da Descrição', 'Tamanho da Descrição (Caracteres)', 'Número de Comentários', 'B_RQ07_descricao_vs_revisoes.png')
    print_header("RQ08: Relação entre as INTERAÇÕES (Participantes) e o NÚMERO DE REVISÕES")
    analyze_correlation(df, 'participants_count', 'comments_count', 'Número de Participantes', 'Número de Comentários')
    plot_correlation_hexbin(df, 'participants_count', 'comments_count', 'Número de Comentários vs. Número de Participantes', 'Número de Participantes', 'Número de Comentários', 'B_RQ08_participantes_vs_revisoes.png')

def print_header(title):
    print("\n" + "*"*len(title))
    print(title)
    print("*"*len(title))
def analyze_group_difference(df, metrica, nome_metrica):
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
    print(f"\nAnalisando a correlação entre '{nome_var1}' e '{nome_var2}'")
    print(f"H0: Não há correlação monotônica entre as variáveis.")
    print(f"H1: Existe correlação monotônica entre as variáveis.")
    corr, p_valor = spearmanr(df[var1], df[var2])
    print(f"Resultado (Spearman): Coeficiente (rho) = {corr:.4f}, p-valor = {p_valor:.5f}")
    if p_valor < 0.05:
        print(f"Conclusão: Rejeitamos H0. Existe uma correlação {'positiva' if corr > 0 else 'negativa'} fraca, mas estatisticamente significativa.")
    else:
        print("Conclusão: Não rejeitamos H0. Não há evidência de correlação.")
def main():
    if not os.path.exists(DATASET_FILE):
        print(f"\nERRO: O arquivo '{DATASET_FILE}' não foi encontrado.")
        return
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"Carregando e preparando o dataset '{DATASET_FILE}'...")
    try:
        df = pd.read_csv(DATASET_FILE, sep=';', quoting=1)
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

if __name__ == "__main__":
    main()
