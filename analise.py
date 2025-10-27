import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

DB_NAME = 'produtos.db'
TABLE_NAME = 'produtos'
CHARTS_DIR = 'charts' 

if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)
    print(f"Pasta '{CHARTS_DIR}' criada.")

print(f'Iniciando análise de "{DB_NAME}"...')

try:
    conn = sqlite3.connect(DB_NAME)
    query = f'SELECT * FROM {TABLE_NAME}'
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print('Erro: O DataFrame está vazio. O banco de dados foi populado?')
        exit()
        
    print(f'Dados carregados')

except Exception as e:
    print(f"Erro ao ler o banco '{DB_NAME}': {e}")
    exit() 

try:
    # Gráfico Top 5 Marcas
    top_brands = df['brand_name'].value_counts().head(5)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_brands.values, y=top_brands.index, palette='viridis')
    plt.title('Top 5 Marcas por Quantidade de Produtos')
    plt.xlabel('Quantidade de Produtos')
    plt.ylabel('Marca')
    
    chart_path_1 = os.path.join(CHARTS_DIR, 'top_brands.png')
    plt.savefig(chart_path_1)
    print(f"Gráfico salvo em '{chart_path_1}'")
    plt.close() 

    # Gráfico Preço Médio por Categoria
    avg_price_category = df.groupby('category')['price'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(x=avg_price_category.values, y=avg_price_category.index, palette='plasma')
    plt.title('Preço Médio por Categoria')
    plt.xlabel('Preço Médio (R$)')
    plt.ylabel('Categoria')
    plt.tight_layout()
    
    chart_path_2 = os.path.join(CHARTS_DIR, 'avg_price_category.png')
    plt.savefig(chart_path_2)
    print(f"Gráfico salvo em '{chart_path_2}'")
    plt.close() 

except Exception as e:
    print(f'Ocorreu um erro: {e}')