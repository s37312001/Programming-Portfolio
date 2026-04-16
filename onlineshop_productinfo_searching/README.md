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

## JSON 格式範例

```json
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
---
## 專案檔案

```text
.
├── PChome.py
└── README.md
