import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException


def sanitize_filename(filename: str) -> str:
    """
    將不適合當作檔名的字元替換掉，避免 Windows 存檔失敗
    例如：\ / : * ? " < > |
    """
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def create_driver():
    """
    建立 Chrome 瀏覽器物件與基本設定
    """
    options = Options()
    options.add_argument("--start-maximized")        # 啟動時最大化視窗
    options.add_argument("--incognito")              # 使用無痕模式
    options.add_argument("--disable-popup-blocking") # 停用彈窗阻擋

    driver = webdriver.Chrome(options=options)
    return driver


def remove_duplicate_products(products: list[dict]) -> list[dict]:
    """
    移除重複商品
    判斷規則：
    只要商品名稱(product_name) + 價格(product_price) 完全一樣，就視為重複

    參數:
        products: 商品資料列表

    回傳:
        去重複後的新列表
    """
    unique_products = []
    seen = set()

    for product in products:
        # 用「商品名稱 + 價格」當作唯一判斷鍵
        key = (product["product_name"], product["product_price"])

        if key not in seen:
            seen.add(key)
            unique_products.append(product)

    return unique_products


def get_product_info(product: str):
    """
    到 PChome 24h 搜尋指定商品，擷取商品資料並輸出 JSON

    功能:
    1. 開啟 PChome 24h
    2. 搜尋使用者輸入的商品名稱
    3. 擷取每頁商品資訊
    4. 翻到下一頁繼續抓
    5. 移除重複商品
    6. 輸出成 JSON 檔案

    參數:
        product: 使用者輸入的商品名稱

    回傳:
        dict: 最終輸出的資料
    """
    driver = create_driver()
    result = []

    try:
        # 進入 PChome 24h 首頁
        driver.get("https://24h.pchome.com.tw/")
        time.sleep(2)

        # 找到搜尋欄並輸入商品名稱
        shopping_form = driver.find_element(By.CSS_SELECTOR, "input.c-search__input")
        shopping_form.clear()
        shopping_form.send_keys(product)

        # 點擊搜尋按鈕
        submit_button = driver.find_element(By.CSS_SELECTOR, "span.btn__square.btn__square--primary")
        submit_button.click()
        time.sleep(3)

        while True:
            # 稍微往下捲動，避免部分資料尚未載入
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 100);")
            time.sleep(2)

            # 取得目前頁面的商品卡片
            elements = driver.find_elements(
                By.CSS_SELECTOR,
                "li.c-listInfoGrid__item.c-listInfoGrid__item--gridCardGray5Rwd"
            )

            # 如果第一頁就沒有資料，直接回傳錯誤訊息
            if not elements and not result:
                return {
                    "title": f"{product}，共 0 筆資料",
                    "keyword": product,
                    "total": 0,
                    "items": [],
                    "message": f"查詢不到商品：{product}"
                }

            # 逐筆擷取商品資料
            for element in elements:
                try:
                    product_name = element.find_element(
                        By.CSS_SELECTOR,
                        ".c-prodInfoV2__title"
                    ).text.strip()

                    product_price = element.find_element(
                        By.CSS_SELECTOR,
                        "div.c-prodInfoV2__priceValue.c-prodInfoV2__priceValue--m"
                    ).text.strip()

                    product_link = element.find_element(
                        By.CSS_SELECTOR,
                        "a.c-prodInfoV2__link.gtmClickV2"
                    ).get_attribute("href")

                    png_link = element.find_element(
                        By.CSS_SELECTOR,
                        "div.c-prodInfoV2__img > img"
                    ).get_attribute("src")

                    result.append({
                        "product_name": product_name,
                        "product_price": product_price,
                        "product_link": product_link,
                        "png_link": png_link
                    })

                except NoSuchElementException:
                    # 單筆資料抓不到就跳過，避免整個程式中斷
                    continue

            # 檢查下一頁按鈕是否存在
            try:
                next_button = driver.find_element(
                    By.CSS_SELECTOR,
                    "span.btn__circular.btn__circular--primary"
                )

                # 如果按鈕有 is-disabled，代表已經是最後一頁
                button_class = next_button.get_attribute("class")
                if "is-disabled" in button_class:
                    break

                # 找箭頭圖示並點擊下一頁
                next_arrow = next_button.find_element(
                    By.CSS_SELECTOR,
                    "i.o-iconFonts.o-iconFonts--arrowSolidRight"
                )
                driver.execute_script("arguments[0].click();", next_arrow)
                time.sleep(3)

            except NoSuchElementException:
                # 找不到下一頁按鈕，代表頁面結束
                break

        # 移除重複商品（商品名稱 + 價格 完全相同才移除）
        unique_results = remove_duplicate_products(result)

        # 計算去重複後的總筆數
        total_count = len(unique_results)

        # 整理輸出的 JSON 結構
        output_data = {
            "title": f"{product}，共 {total_count} 筆資料",
            "keyword": product,
            "total": total_count,
            "items": unique_results
        }

        # 產生安全檔名
        safe_filename = sanitize_filename(f"{product}_{total_count}筆資料")

        # 輸出 JSON 檔案
        with open(f"{safe_filename}.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        return output_data

    except WebDriverException as e:
        # 瀏覽器或 Selenium 執行出錯時回傳錯誤訊息
        return {
            "title": f"{product}，共 0 筆資料",
            "keyword": product,
            "total": 0,
            "items": [],
            "message": f"發生瀏覽器錯誤：{str(e)}"
        }

    finally:
        # 不論成功或失敗都關閉瀏覽器
        driver.quit()


if __name__ == "__main__":
    # 先讓使用者輸入要搜尋的產品名稱
    keyword = input("請輸入要搜尋的產品名稱：").strip()

    # 檢查使用者是否有輸入內容
    if not keyword:
        print("你沒有輸入產品名稱，程式結束。")
    else:
        # 開始查詢
        data = get_product_info(keyword)

        # 將結果印在終端機
        print(json.dumps(data, ensure_ascii=False, indent=4))