# PChome 商品搜尋爬蟲

這是一個使用 Python + Selenium 撰寫的商品搜尋程式。

使用者在執行程式時，可以先輸入想搜尋的產品名稱，程式會自動到 PChome 24h 搜尋商品，抓取商品資訊，移除重複資料後，最後輸出成 JSON 檔案。

---

## 功能說明

本程式包含以下功能：

- 執行時先輸入要搜尋的產品名稱
- 自動前往 PChome 24h 搜尋商品
- 擷取商品資訊：
  - 商品名稱
  - 商品價格
  - 商品連結
  - 商品圖片連結
- 自動翻頁抓取多頁資料
- 自動移除重複商品
  - 判斷規則：**商品名稱 + 價格 都完全相同**
- 產生 JSON 檔案
- JSON 標題會顯示：
  - 使用者輸入的產品名稱
  - 總共有幾筆資料

---

## 專案檔案

```text
.
├── PChome.py
└── README.md

安裝需求

請先安裝以下套件：

pip install selenium

另外請先確認：

已安裝 Google Chrome
ChromeDriver 版本與 Chrome 瀏覽器版本相容
已安裝 Python 3
使用方式

在終端機執行：

python PChome.py

執行後，畫面會要求你輸入想搜尋的產品名稱，例如：

請輸入要搜尋的產品名稱：延長線

輸入後，程式會開始搜尋並抓取資料。

輸出結果

程式會輸出一個 JSON 檔案。

例如你輸入：

延長線

若最後抓到並去重複後共有 15 筆資料，檔名可能會是：

延長線_15筆資料.json
JSON 格式範例
{
    "title": "延長線，共 15 筆資料",
    "keyword": "延長線",
    "total": 15,
    "items": [
        {
            "product_name": "商品A",
            "product_price": "399",
            "product_link": "https://...",
            "png_link": "https://..."
        },
        {
            "product_name": "商品B",
            "product_price": "599",
            "product_link": "https://...",
            "png_link": "https://..."
        }
    ]
}
去重複規則

當兩筆資料符合以下條件時，會被視為重複商品，只保留第一筆：

product_name 完全相同
product_price 完全相同

也就是說：

名稱一樣、價格也一樣 → 視為重複
名稱一樣、價格不同 → 不算重複
名稱不同、價格一樣 → 不算重複
程式流程
使用者輸入產品名稱
開啟 PChome 24h 首頁
在搜尋欄輸入產品名稱
點擊搜尋
擷取目前頁面的商品資料
點擊下一頁繼續擷取
將所有資料整理完成
移除重複商品
輸出 JSON 檔案
主要函式說明
sanitize_filename(filename)

將不適合用在檔名中的特殊字元替換掉，避免存檔失敗。

create_driver()

建立 Chrome 瀏覽器物件與基本設定。

remove_duplicate_products(products)

依照「商品名稱 + 價格」移除重複商品。

get_product_info(product)

執行搜尋、抓取商品資料、去重複、輸出 JSON。

注意事項
若網站版面或 CSS Selector 改變，程式可能需要修改。
若網路較慢，可能需要增加等待時間。
若搜尋結果很多，抓取時間會較久。
若查無資料，程式仍會回傳 JSON 結構，但 total 會是 0。
執行成功後你會得到什麼
終端機顯示 JSON 結果
資料夾中產生 .json 檔案
JSON 第一層標題會顯示：
你輸入的產品名稱
去重複後的總筆數
可再延伸優化的方向

未來可以再加入：

匯出成 CSV / Excel
價格排序
限制只抓前幾頁
加入更多商品欄位
改成 Flask 網頁版搜尋介面
