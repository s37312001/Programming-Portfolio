# PChome Product Info Web Scraping

這是一個使用 **Python + Selenium** 撰寫的 PChome 24h 購物商品資訊爬蟲程式。
程式會自動開啟 Chrome 瀏覽器，進入 PChome 24h 購物網站，搜尋指定商品關鍵字，並擷取搜尋結果中的商品資訊，最後輸出成 JSON 檔案。

---

## 專案功能

本程式目前可以自動取得 PChome 搜尋結果中的以下資訊：

- 商品名稱
- 商品價格
- 商品頁面連結
- 商品圖片連結

搜尋完成後，程式會將結果儲存成：

```text
{商品關鍵字}.json
```

例如目前程式預設搜尋：

```python
get_product_info("延長線")
```

執行後會產生：

```text
延長線.json
```

---

## 使用技術

- Python
- Selenium
- Chrome WebDriver
- JSON

---

## 專案結構

```text
project/
│
├── PChome_productinfo_webscraping.py
└── README.md
```

---

## 環境需求

執行本程式前，請先確認電腦已安裝：

- Python 3.x
- Google Chrome 瀏覽器
- Selenium 套件

---

## 安裝方式

### 1. 安裝 Selenium

在終端機或命令提示字元中執行：

```bash
pip install selenium
```

### 2. 確認 Chrome 已安裝

本程式會使用 Chrome 瀏覽器進行自動化操作，因此電腦需要先安裝 Google Chrome。

若使用新版 Selenium，通常可以透過 Selenium Manager 自動管理對應版本的 ChromeDriver。
如果執行時出現 WebDriver 相關錯誤，請檢查 Selenium 版本、Chrome 版本，或手動安裝對應的 ChromeDriver。

---

## 執行方式

在專案資料夾中執行：

```bash
python PChome_productinfo_webscraping.py
```

目前程式最後一行預設為：

```python
print(get_product_info("延長線"))
```

因此執行後，程式會自動搜尋「延長線」這個關鍵字。

---

## 如何修改搜尋商品

如果想搜尋其他商品，可以修改程式最後一行：

```python
print(get_product_info("延長線"))
```

例如改成搜尋「筆電」：

```python
print(get_product_info("筆電"))
```

執行後會產生：

```text
筆電.json
```

---

## 輸出格式

程式會將搜尋結果儲存為 JSON 格式。
每一筆商品資料包含以下欄位：

```json
{
    "product_name": "商品名稱",
    "product_price": "商品價格",
    "product_link": "商品頁面連結",
    "png_link": "商品圖片連結"
}
```

輸出範例：

```json
[
    {
        "product_name": "延長線商品範例",
        "product_price": "399",
        "product_link": "https://24h.pchome.com.tw/...",
        "png_link": "https://cs-a.ecimg.tw/..."
    }
]
```

---

## 程式流程說明

### 1. 設定 Chrome 瀏覽器選項

程式會設定以下 Chrome 啟動選項：

```python
options.add_argument("--start-maximized")
options.add_argument("--incognito")
options.add_argument("--disable-popup-blocking")
```

用途分別為：

- 開啟瀏覽器時最大化視窗
- 使用無痕模式
- 停用彈出視窗阻擋功能

---

### 2. 開啟 PChome 24h 首頁

```python
driver.get("https://24h.pchome.com.tw/")
```

程式會進入 PChome 24h 購物網站首頁。

---

### 3. 搜尋商品

程式會找到搜尋欄位，輸入商品關鍵字，並點擊搜尋按鈕。

```python
shopping_form = driver.find_element(By.CSS_SELECTOR, "input.c-search__input")
shopping_form.send_keys(product)
```

---

### 4. 擷取商品資訊

程式會擷取每一個商品卡片中的：

- 商品名稱
- 商品價格
- 商品連結
- 商品圖片連結

並將資料加入 `result` 清單中。

---

### 5. 自動換頁

程式會點擊下一頁按鈕，直到找不到下一頁或下一頁按鈕變成停用狀態為止。

---

### 6. 輸出 JSON 檔案

搜尋完成後，程式會將結果寫入 JSON 檔案：

```python
with open(f"{product}.json", "w", encoding="utf8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)
```

其中 `ensure_ascii=False` 可以避免中文字被轉成 Unicode 編碼，讓 JSON 檔案更容易閱讀。

---

## 錯誤處理

如果搜尋不到商品，程式會回傳錯誤訊息：

```json
{
    "error": "查詢不到商品：商品名稱"
}
```

在擷取單一商品資訊時，如果某筆商品缺少部分欄位，程式會略過該筆資料並繼續執行：

```python
except Exception:
    continue
```

---

## 注意事項

1. 網頁結構可能改變本程式依賴 PChome 網頁的 CSS Selector。如果 PChome 改版，可能會導致爬蟲找不到元素，需要更新 selector。
2. 若未來想讓這個檔案可以被其他程式 import，建議改成：

   ```python
   if __name__ == "__main__":
       print(get_product_info("延長線"))
   ```
3. 請合理使用爬蟲，執行爬蟲時請避免過度頻繁請求，並遵守網站的使用規範。

---

## 可改進方向

未來可以考慮加入以下功能：

- 讓使用者從命令列輸入商品名稱
- 加入 `driver.quit()`，確保瀏覽器正確關閉
- 將等待方式從 `time.sleep()` 改成 Selenium 的 `WebDriverWait`
- 加入錯誤日誌紀錄
- 將結果同時輸出成 CSV
- 增加價格排序或篩選功能
- 建立簡單的 Streamlit 介面，讓使用者可以在網頁上輸入商品名稱並下載結果

---

## 參考執行範例

```bash
python PChome_productinfo_webscraping.py
```

執行後會：

1. 開啟 Chrome 瀏覽器
2. 進入 PChome 24h 購物
3. 搜尋「延長線」
4. 擷取商品資訊
5. 換頁直到最後一頁
6. 產生 `延長線.json`

---

## 專案目的

本專案主要用於練習：

- Selenium 網頁自動化
- 電商商品資料擷取
- CSS Selector 定位網頁元素
- JSON 資料輸出
- Python 函式封裝與錯誤處理
