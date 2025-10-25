import requests
import re

def main():
    try:
        response = requests.get("https://ge.globo.com/")
        if response.status_code == 200:
            print("✅ Requisição bem-sucedida!")
            print("Resposta da API do GitHub:")
            print(response.json()["current_user_url"])
        else:
            print(f"⚠️ Erro na requisição: {response.status_code}")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")

def get_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)

        if match:
            title = match.group(1).strip()
            print(f"✅ Título da página: {title}")
        else:
            print("⚠️ Nenhum título encontrado.")
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")

if __name__ == "__main__":
    #main()
    site = input(f'Digite a url do site: ')
    get_title(site)
