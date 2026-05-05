# Laplacian應用:商品照片模糊比對小工具

## 1. 研究目的

目標是利用Laplacian計算商品照片的模糊程度，協助產品上架人員審核大量商品照片。

人工審核時，不同人對「模糊」的判斷可能不一致，因此這個工具希望用同一個計算方式產生清晰度分數，再依照使用者設定的模糊判斷標準，自動把照片分類到：

```text
ok/      清晰度達標
fail/    清晰度未達標，或圖片讀取失敗
```

這樣可以：

- 減少人工逐張判斷照片的時間
- 建立比較一致的模糊判斷標準
- 將商品照片依結果自動移動到不同資料夾
- 產生 CSV 報表，方便後續追蹤每張照片的分數與分類原因

> 注意：Laplacian variance 是傳統影像處理方法，不是機器學習模型。它不需要訓練資料，但 threshold 需要依照實際照片類型調整。

---

## 2. 程式碼架構

```text
laplacian_blur_classifier/
├── app.py                         # Streamlit 介面主程式
├── blur_core.py                   # Laplacian 計算、建立資料夾、移動檔案、輸出報表
├── requirements.txt               # Streamlit 需要的套件
├── run_app.bat                    # Windows 可雙擊啟動 Streamlit
└── README.md                      # 說明文件
```

### `app.py`

負責畫面操作：

- 輸入店家名稱
- 選擇日期
- 選擇來源照片資料夾
- 選擇結果存放位置
- 用滑桿選擇模糊判斷標準
- 顯示處理進度
- 顯示 ok / fail 統計
- 顯示與下載 CSV 報表

### `blur_core.py`

負責核心邏輯：

- 只抓 `.jpg`、`.jpeg`、`.png`
- 讀取圖片
- 計算 Laplacian 分數
- 判斷 ok / fail
- 直接移動照片，不複製照片
- 建立 `店家名稱_年月日` 結果資料夾
- 在結果資料夾底下建立 `ok` 和 `fail`
- 將圖片讀取失敗的照片移到 `fail`
- 輸出 `classification_report.csv`

---

## 3. 執行方式

### 3.1 第一次使用需要安裝套件

Streamlit、OpenCV、pandas、numpy 仍然需要先安裝一次。如果電腦已經安裝過，就不用重複安裝。

```bash
pip install -r requirements.txt
```

### 3.2 啟動 Streamlit 介面

```bash
streamlit run app.py
```

Windows 使用者也可以直接雙擊：

```text
run_app.bat
```

---

## 4. 使用流程

1. 開啟 Streamlit 畫面。
2. 輸入店家名稱，例如：`竹君烘焙房`。
3. 確認日期，預設是今天。
4. 選擇或貼上「來源照片資料夾位置」。
5. 選擇或貼上「結果存放位置」。
6. 用滑桿調整「模糊判斷標準」。
7. 按下「開始移動並分類照片」。
8. 程式會建立結果資料夾，例如：

```text
竹君烘焙房_20260505/
├── ok/
├── fail/
└── classification_report.csv
```

如果同一天同店家已經執行過，程式會自動加流水號，避免覆蓋舊資料：

```text
小王寵物店_20260505_02/
小王寵物店_20260505_03/
```

---

## 5. 模糊判斷標準怎麼看？

程式使用 Laplacian 分數判斷照片清楚程度：

```text
分數 >= 模糊判斷標準  → ok
分數 <  模糊判斷標準  → fail
```

滑桿越往右，標準越嚴格，更多照片會進 `fail`。

滑桿越往左，標準越寬鬆，只有非常模糊的照片才會進 `fail`。

建議說明：

```text
100 ~ 300    很寬鬆：只有非常模糊的照片才會進 fail
350 ~ 600    偏寬鬆：適合先快速抓出明顯模糊的照片
650 ~ 800    一般建議：適合商品照初步篩選。
850 ~ 1100   偏嚴格：照片需要較清楚的文字、邊緣或紋理
1150 以上    非常嚴格：稍微不清楚也可能進 fail
```

---

## 6. Laplacian 原理

Laplacian 是一種邊緣偵測方法。照片清楚時，文字、線條、商品邊界、紋理通常會有明顯的灰階變化；照片模糊時，這些邊界會被抹平，灰階變化會變少。

本程式核心概念如下：

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
score = cv2.Laplacian(gray, cv2.CV_64F).var()
```

流程：

1. 先把彩色圖片轉成灰階。
2. 使用 `cv2.Laplacian()` 找出影像中變化較明顯的邊緣。
3. 使用 `.var()` 計算方差。
4. 方差越高，通常代表邊緣越清楚。
5. 方差越低，通常代表照片越模糊。

簡化理解：

```text
照片清楚 → 邊緣多、文字銳利 → Laplacian 分數高
照片模糊 → 邊緣少、文字糊掉 → Laplacian 分數低
```

---

## 7. 圖片讀取失敗處理

這個版本只處理：

```text
.jpg
.jpeg
.png
```

如果副檔名是以上三種，但圖片壞掉、格式異常，或 OpenCV 無法讀取，程式不會中斷整批流程，而是會直接把該檔案移到：

```text
fail/
```

CSV 報表中會顯示原因：

```text
圖片讀取失敗，已移到 fail
```

非 jpg / jpeg / png 的檔案，例如 Excel、PDF、txt，不會被移動，避免誤搬非照片檔。

---


## 8. 使用上的心得與建議

1. **因為本程式會直接移動檔案，建議第一次先用測試資料夾操作**
   確定流程與結果符合需求後，再用正式商品照片。
3. **建議先用少量照片測試 threshold** 例如先放 20 張照片，觀察 `ok` 與 `fail` 是否符合人工直覺，再決定正式大量處理。
4. **Laplacian 適合當第一層篩選** 它可以快速抓出明顯模糊的照片，但不一定能判斷構圖、曝光、商品是否完整入鏡。因此正式審核仍建議保留人工複查。

---

## 10. 參考來源

- PyImageSearch - Blur detection with OpenCV https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
- CSDN 中文參考文章 https://blog.csdn.net/WZZ18191171661/article/details/96602043
