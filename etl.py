import requests
import re
import json
import time
import pandas as pd
import sqlite3

API_BASE_URL = 'https://api.devmka.online/products'

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

            time.sleep(0.1)

    except requests.RequestException as e:
        print(f'Erro ao acessar API na página: {e}')
        return []

    for produto in todos_os_produtos:
        produto['product_url'] = f'https://testdata.devmka.online/products/{produto['id']}'

    print(f'Extração concluída. {len(todos_os_produtos)} produtos encontrados.')
    return todos_os_produtos

def main():
    try:
        ...
    except Exception as e:
        print(f'')

if __name__ == '__main__':
    # main()
    extrair_dados()