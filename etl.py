import requests
import re

def main():
    try:
        ...
    except Exception as e:
        print(f'')

def get_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE|re.DOTALL)

        if match:
            title = match.group(1).strip()
            print(f'Título da página: {title}')
        else:
            print('Nenhum título encontrado.')
    except Exception as e:
        print(f'Erro ao acessar: {e}')

if __name__ == '__main__':
    site = input(f'Digite a url do site: ')
    get_title(site)
