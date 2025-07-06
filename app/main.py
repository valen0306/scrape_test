# 必要なライブラリをインポートします
import requests
from bs4 import BeautifulSoup
import urllib.parse
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Scrape Anzeninfo"}

@app.get("/scrape/anzeninfo")
async def scrape_anzeninfo():
    target_url = 'https://anzeninfo.mhlw.go.jp/anzen_pg/sai_fnd.aspx'
    # target_url = 'https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_LST.aspx'
    try:
        response = requests.get(target_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a')
        url_list = []
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href and not href.startswith('javascript:') and href.strip():
                absolute_url = urllib.parse.urljoin(target_url, href)
        return url_list
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
