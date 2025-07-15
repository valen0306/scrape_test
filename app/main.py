from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Scrape Anzeninfo with Selenium"}

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

@app.get("/scrape")
async def scrape():
    data = scrape_mhlw_anzeninfo_api()
    return JSONResponse(content=data)

def scrape_mhlw_anzeninfo_api():
    driver = None
    all_case_links = []
    try:
        driver = webdriver.Chrome()
        url = "https://anzeninfo.mhlw.go.jp/anzen_pg/sai_fnd.aspx"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "srchButton"))
        )
        # --- 1. 「業種」のアコーディオンを展開する ---
        try:
            industry_accordion_header = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='accTitle_Industry']"))
            )
            industry_accordion_header.click()
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "acc_Industry_content"))
            )
            time.sleep(1)
        except TimeoutException:
            return []
        # --- 2. 「建設業」のチェックボックスを選択する ---
        try:
            construction_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), '建設業')]/preceding-sibling::input[@type='checkbox']"))
            )
            if not construction_checkbox.is_selected():
                construction_checkbox.click()
        except (TimeoutException, NoSuchElementException):
            return []
        # --- 3. 「検索開始」ボタンをクリックする ---
        try:
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "srchButton"))
            )
            search_button.click()
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "pgMain"))
            )
            time.sleep(2)
        except TimeoutException:
            return []
        # --- 4. 検索結果ページから各事例へのリンクを抽出する ---
        page_num = 1
        while True:
            try:
                case_elements = driver.find_elements(By.XPATH, "//div[@class='pgMain']//td[@class='td0']//a")
                if not case_elements:
                    break
                for element in case_elements:
                    link_url = element.get_attribute('href')
                    link_text = element.text.strip()
                    if link_url and link_text:
                        all_case_links.append({'title': link_text, 'url': link_url})
                # 次のページへのリンクを探す
                next_page_link = None
                try:
                    next_page_button = driver.find_element(By.XPATH, "//img[@alt='次へ']")
                    parent_a_tag = next_page_button.find_element(By.XPATH, "./parent::a")
                    next_page_link = parent_a_tag.get_attribute('href')
                except NoSuchElementException:
                    break
                if next_page_link:
                    driver.execute_script(f"location.href='{next_page_link}'")
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, "pgMain"))
                    )
                    time.sleep(2)
                    page_num += 1
                else:
                    break
            except Exception:
                break
    finally:
        if driver:
            driver.quit()
    return all_case_links