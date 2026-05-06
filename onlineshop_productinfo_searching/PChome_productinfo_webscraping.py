import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_product_info(product):
    # 設定 Chrome 瀏覽器的選項
    options = Options()
    options.add_argument("--start-maximized") # Chrome 瀏覽器在啟動時最大化視窗
    options.add_argument("--incognito") # 無痕模式
    options.add_argument("--disable-popup-blocking") # 停用 Chrome 的彈窗阻擋功能。

    # 建立 Chrome 瀏覽器物件
    driver = webdriver.Chrome(options=options) #整個瀏覽器視窗
    driver.get("https://24h.pchome.com.tw/") #要訪問到哪一個網址
    time.sleep(2)

    #搜尋商品
    shopping_form = driver.find_element(By.CSS_SELECTOR, "input.c-search__input")
    shopping_form.send_keys(product) 
    
    #點擊搜尋按鈕
    submit_button = driver.find_element(By.CSS_SELECTOR, "span.btn__square.btn__square--primary")
    submit_button.click()
    time.sleep(2)
    
    result = []

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-100);")
        time.sleep(2)

        elements = driver.find_elements(By.CSS_SELECTOR, "div.c-listInfoGrid.c-listInfoGrid--gridCard li.c-listInfoGrid__item.c-listInfoGrid__item--gridCardGray5Rwd")
    
        # 查詢不到商品時，直接回傳錯誤訊息
        if not elements and not result:
            return {"error": f"查詢不到商品：{product}"}

        for element in elements:
            try:
                product_name = element.find_element(By.CSS_SELECTOR, '.c-prodInfoV2__title').text
                product_price = element.find_element(By.CSS_SELECTOR, 'div.c-prodInfoV2__priceValue.c-prodInfoV2__priceValue--m').text
                product_link = element.find_element(By.CSS_SELECTOR, 'a.c-prodInfoV2__link.gtmClickV2').get_attribute('href')
                png_link = element.find_element(By.CSS_SELECTOR, 'div.c-prodInfoV2__img > img').get_attribute('src')

                result.append({
                    "product_name": product_name,
                    "product_price": product_price,
                    "product_link": product_link,
                    "png_link" : png_link
                })
            except Exception:
                continue

        next_button = driver.find_element(By.CSS_SELECTOR, "span.btn__circular.btn__circular--primary i.o-iconFonts.o-iconFonts--arrowSolidRight")
        next_button.click()
        time.sleep(2)       
        disabled_buttons = driver.find_elements(By.CSS_SELECTOR,"span.btn__circular.btn__circular--primary.is-disabled")
        if disabled_buttons: break

    with open(f"{product}.json", "w", encoding="utf8") as f:
        json.dump(result, f, indent = 4, ensure_ascii = False)               

    return result


print(get_product_info("延長線"))