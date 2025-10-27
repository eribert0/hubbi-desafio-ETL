import requests
import re
import json
import time
import pandas as pd
import sqlite3
import os

API_BASE_URL = 'https://api.devmka.online/products'
DB_NAME = 'produtos.db'
CSV_NAME = 'produtos.csv'
CACHE_FILE = 'dados_brutos.json'

def extrair_dados():
    print('Iniciando extração de dados...')

    todos_os_produtos = []

    params={
        'page': 1,
        'limit': 12
    }

    try:
        resposta = requests.get(API_BASE_URL, params=params)
        resposta.raise_for_status()
        data = resposta.json()

        todos_os_produtos.extend(data['data'])

        total_de_paginas = data['meta']['last_page']
        print(f'total de páginas a coletar: {total_de_paginas}')
    
        for pagina in range(2, total_de_paginas+1):
            print(f'Coletando página {pagina} de {total_de_paginas}')
            params['page'] = pagina

            resposta_loop = requests.get(API_BASE_URL, params=params)
            resposta_loop.raise_for_status()

            produtos_da_pagina = resposta_loop.json()['data']
            todos_os_produtos.extend(produtos_da_pagina)

            time.sleep(0.1) # prevenção de rate limiting

    except requests.RequestException as e:
        print(f'Erro ao acessar API na página: {e}')
        return []

    for produto in todos_os_produtos:
        produto['product_url'] = f'https://testdata.devmka.online/products/{produto['id']}'

    print(f'Extração concluída. {len(todos_os_produtos)} produtos encontrados.')
    return todos_os_produtos

def tratar_dados(dados_brutos:list):
    print(f'Tratando os dados...')
    if not dados_brutos:
        print(f'Nenhum dado para tratar')
        return pd.DataFrame()

    df = pd.DataFrame(dados_brutos)

    df['category'] = df['category'].apply(lambda x: x['name'])
    df['title'] = df['title'].str.upper()
    df['brand'] = df['brand'].str.upper()
    df['title'] = df['title'].apply(lambda x: ' '.join(x.split(' ')[:-1]))
    df.drop_duplicates(subset=['id'], inplace=True)

    # Parte de especificações
    df['gross_weight'] = df['specifications'].str.extract(r'Peso Bruto: (\d+\.?\d*)kg').astype(float)
    df[['width', 'length']] = df['specifications'].str.extract(r'Dimensões \(LxC\): (\d+\.?\d*)cm x (\d+\.?\d*)cm').astype(float)
    df['material'] = df['specifications'].str.extract(r'Material Principal: ([^|]+)', expand=False).str.strip()
    df['warranty'] = df['specifications'].str.extract(r'Garantia do Fabricante: ([^|$]+)', expand=False).str.strip()

    print(f'DataFrame iniciado. Informações: ')
    print(df.info())

    print(f'\n5 primeiras linhas: ')
    print(df.head())

    print(df[['title', 'gross_weight', 'width', 'length', 'material', 'warranty']].head())
    
    df_final = df.rename(columns={
        'title':'name',
        'product_url':'product_url',
        'part_number': 'part_number',
        'brand': 'brand_name',
        'category': 'category',
        'gross_weight': 'gross_weight',
        'width': 'width',
        'length': 'length',
        'warranty': 'warranty',
        'material': 'material',
        'thumbnail': 'photo_url',
        'stock_quantity': 'stock_quantity'
    })

    colunas_finais = [
        'name', 'product_url', 'part_number', 'brand_name', 'category',
        'gross_weight', 'width', 'length', 'warranty', 'material', 
        'photo_url', 'stock_quantity', 'price' 
    ]

    df_final = df_final[colunas_finais]

    print("DataFrame final limpo e pronto para carga.")
    print(df_final.info())
    return df_final

def carregar_dados(df: pd.DataFrame):
    print(f'Carga dos dados...')

    if df.empty:
        print('Nenhum dado para carregar')
        return
    
    try:
        connection = sqlite3.connect(DB_NAME)
        df.to_sql('produtos', connection, if_exists='replace', index=False)
        
        print(f'Dados carregados em {DB_NAME}')
        connection.close()
        
    except Exception as e:
        print(f'Erro ao salvar: {e}')

    try:
        df.to_csv(CSV_NAME, index=False, encoding='utf-8')
        print(f"Dados carregados com sucesso em '{CSV_NAME}'")
    except Exception as e:
        print(f"Erro ao salvar no CSV: {e}")

def main():
    print('Script Pipeline ETL')
    produtos = [] 

    if os.path.exists(CACHE_FILE):
        print('Encontrado cache local. Carregando dados...')
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            produtos = json.load(f)
        print(f'{len(produtos)} produtos carregados.')
    else:
        print('Cache não encontrado. Iniciando extração da API...')
        produtos = extrair_dados()
        
        if produtos:
            print(f'Salvando dados em {CACHE_FILE}...')
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(produtos, f, ensure_ascii=False, indent=2)
            print('Cache salvo com sucesso.')
    
    if produtos:
        df_produtos = tratar_dados(produtos)
        carregar_dados(df_produtos)
    else:
        print('Nenhum produto encontrado para processar.')
    
    print('Pipeline ETL concluído.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Erro no pipeline: {e}')
