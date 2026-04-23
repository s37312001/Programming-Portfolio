# PM小老師 `app.py` 使用說明

## 1. 專案簡介

本專案是一個以 **Streamlit** 製作的互動式問答系統，名稱為 **PM小老師**。
它的目的是協助 **Junior PM** ，根據歷史客訴案例與既有處理方案，快速找到可以參考的排查方向，並透過 **Ollama 本地大語言模型**，將檢索到的資料整理成較自然、較像主管帶新人的回答。

此程式的核心流程如下：

1. 讀取 CFPB CSV 案例資料 (可以載入其他的資料集)
2. 建立可比對的檢索文本
3. 對使用者問題做文字清理與斷詞
4. 使用 TF-IDF + cosine similarity 找出相似案例
5. 過濾掉過度重複的解法
6. 組成 prompt 丟給 Ollama
7. 在 Streamlit UI 顯示最終回答與參考來源

---

## 2. 需要先安裝哪些工具

### 2.1 基本環境

建議環境：

- Python 3.10 以上
- pip
- 終端機 / Terminal / Command Prompt
- 本地 Ollama

### 2.2 Python 套件安裝

請先在 terminal 執行：

```bash
pip install pandas requests streamlit opencc-python-reimplemented scikit-learn
```

### 2.3 需要安裝的外部工具

除了 Python 套件，這份程式還需要：

#### (1) Ollama

用途：在本機執行大語言模型，讓系統可以把檢索結果整理成自然語言回答。

請先安裝 Ollama (https://ollama.com/download)。

#### (2) Ollama 模型

這份程式預設模型為：

```python
OLLAMA_MODEL = "qwen2.5:7b-instruct"
```

所以需要先拉下模型：

```bash
ollama pull qwen2.5:7b-instruct
```

#### (3) CSV 資料檔

程式預設讀取：

```python
DEFAULT_CSV_PATH = "complaints_final.csv"
```

因此請確認：

- `complaints_final.csv` 與 `app.py` 放在同一層資料夾，或把 `DEFAULT_CSV_PATH` 改成正確路徑

---

## 3. 本專案使用到的主要套件與用途

| 套件                                                | 用途                     |
| --------------------------------------------------- | ------------------------ |
| `re`                                              | 文字清理、正規表示式處理 |
| `typing.List`                                     | 讓函式型別註記更清楚     |
| `pandas`                                          | 讀取與整理 CSV 資料      |
| `requests`                                        | 呼叫 Ollama API          |
| `streamlit`                                       | 建立網頁 UI 介面         |
| `opencc`                                          | 將文字轉成繁體中文       |
| `sklearn.feature_extraction.text.TfidfVectorizer` | 建立文字向量表示         |
| `sklearn.metrics.pairwise.cosine_similarity`      | 計算相似度               |

---

## 4. 程式架構總覽

本程式大致可以分成 6 個模組：

1. **基本設定**：設定 Ollama API、模型名稱、CSV 路徑、頁面標題
2. **文字前處理**：標準化文字、分詞、建立關鍵字比對
3. **檢索文本建立**：把每筆案例整理成一份可搜尋的文件
4. **相似案例排序**：找出與使用者問題最接近的案例
5. **Prompt 與 LLM 呼叫**：把案例整理後交給 Ollama 產生回答
6. **Streamlit UI**：讓使用者輸入問題並查看結果

---

## 5. 自定義函式說明（包含製作原因）

以下為 `app.py` 中的重要自定義函式與設計原因。

---

### 5.1 `normalize_text(text: str) -> str`

**功能：**

- 將文字轉小寫
- 去除前後空白
- 移除特殊符號
- 將多餘空白合併成單一空格

**為什麼要做：**
原始問題文字常會有標點、大小寫、雜訊字元。
如果不先做清理，後續比對相似案例時容易因格式不同而降低準確度。

**教學重點：**

```python
text = re.sub(r"[^\w\u4e00-\u9fff\s]", " ", text)
```

這行使用正規表示式保留：

- 英數字
- 中文
- 空白

---

### 5.2 `tokenize(text: str) -> List[str]`

**功能：**

- 對中英文文字做簡易斷詞
- 中文用 2~4 字 n-gram 切分
- 英文抓取英數 token
- 過濾 stopwords 與過短 token

**為什麼要做：**
這份專案不是用大型中文斷詞器，而是希望保留**輕量、好部署**的作法。
使用 n-gram 的方式可以在不額外依賴中文 NLP 套件的情況下，保留一定程度的語意重疊判斷能力。

**教學重點：**

```python
for n in [2, 3, 4]:
    for i in range(len(block) - n + 1):
        zh_tokens.append(block[i:i + n])
```

這段是在生成中文 2-gram、3-gram、4-gram。

---

### 5.3 `normalize_solution_text(text: str) -> str`

**功能：**

- 將解決方案中的金額、數字做統一化
- 清理標點與多餘空白

**為什麼要做：**
不同案例的解法可能只是金額、筆數不同，但實際上流程很像。
先把金額與數字抽象化成「金額」「數字」，有助於判斷兩個方案是不是本質上重複。

**教學重點：**

```python
text = re.sub(r"\$[\d,]+(\.\d+)?", "金額", text)
text = re.sub(r"\d+(\.\d+)?", "數字", text)
```

---

### 5.4 `solution_similarity(sol1: str, sol2: str) -> float`

**功能：**

- 計算兩個解決方案之間的重疊程度
- 用 token 交集比例衡量是否相似

**為什麼要做：**
即使找到很多相似案例，也可能出現三筆幾乎相同的答案。
這個函式用來去除重複性太高的方案，讓最後展示給使用者的參考來源更多元。

---

### 5.5 `keyword_overlap_score(question: str, case_doc: str) -> float`

**功能：**

- 計算使用者問題與案例文件的關鍵字重疊比例

**為什麼要做：**
單純靠 TF-IDF 相似度有時會被字形影響。
加入關鍵字重疊分數(採用交集合)，可以讓排序更貼近人類直覺，提升檢索穩定度。

---

### 5.6 `build_case_document(row: pd.Series) -> str`

**功能：**

- 把每筆案例的重要欄位串接成一份檢索文件

包含：

- `Issue`
- `Sub-issue`
- `Consumer complaint narrative in Chinese`
- `Solution in Chinese`

**為什麼要做：**
如果只看單一欄位，資訊可能不完整。
把「問題分類 + 中文敘述 + 解法」合併後，能讓系統在搜尋相似案例時參考更多上下文。

**注意：**
程式中這兩個欄位被重複加入兩次：

```python
str(row.get("Consumer complaint narrative in Chinese", "")),
str(row.get("Consumer complaint narrative in Chinese", "")),
str(row.get("Solution in Chinese", "")),
str(row.get("Solution in Chinese", ""))
```

這種把中文欄位重複一次的寫法，這樣中文敘述和中文解法會更容易被抓到。

---

### 5.7 `rank_cases(question: str, df: pd.DataFrame, top_k: int = 3) -> pd.DataFrame`

**功能：**

- 建立語料庫
- 用 TF-IDF 向量化
- 用 cosine similarity 算問題與各案例的相似度
- 混合 keyword overlap score
- 依最終分數排序
- 去除相似解法
- 取前 `top_k` 筆

**為什麼要做：**
這是整個系統最核心的「檢索層」。
它決定後面丟給 Ollama 的資料品質，因此會直接影響最終回答的可信度與實用性。

**分數設計：**

```python
final_score = (sim * 0.7) + (keyword_score * 0.3)
```

表示：

- 70% 來自 TF-IDF 相似度
- 30% 來自關鍵字重疊

這種混合式設計能兼顧統計比對與規則比對。

**教學重點：**

```python
vectorizer = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(2, 4),
    min_df=1
)
```

這裡使用：

- `char_wb`：以字元邊界建立 n-gram
- `ngram_range=(2,4)`：抓 2~4 字片段

對中英混合、錯字容忍、簡易中文比對都很實用。

---

### 5.8 `build_prompt(question: str, top_results: pd.DataFrame) -> str`

**功能：**

- 將檢索到的方案整理成 prompt
- 明確規定模型輸出風格與格式

**為什麼要做：**
如果沒有良好的 prompt，LLM 很容易：

- 回答太空泛
- 混入不相關內容
- 使用非台灣慣用詞
- 直接照抄資料原文

因此這個函式的目的是 **把模型輸出限制在你要的範圍內**。

**這份 prompt 的設計重點：**

- 只用繁體中文
- 先理解問題
- 再給 3 個排查方向
- 忽略明顯不相關方案
- 要像主管帶新人，不要像教科書

---

### 5.9 `ask_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 180) -> str`

**功能：**

- 將 prompt 送到本地 Ollama API
- 取得模型回答
- 用 OpenCC 轉成繁體中文
- 處理錯誤訊息

**為什麼要做：**
把模型呼叫獨立成函式後，程式會比較模組化，也方便後續換模型或調整 timeout。

**教學重點：**

```python
response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
```

以及錯誤處理：

- `ConnectionError`
- `Timeout`
- `HTTPError`
- 其他例外

這是很好的實務寫法，因為模型服務很常遇到沒開、太慢、回傳失敗等問題。

---

### 5.10 `pm_ai_assistant(question: str, df: pd.DataFrame, top_k: int = 3)`

**功能：**

- 串起 `rank_cases()`、`build_prompt()`、`ask_ollama()`
- 回傳最終回答與相似案例

**為什麼要做：**
這是一個整合流程的函式，讓主程式在需要時可以一行完成整段邏輯。
雖然在 UI 目前是分開呼叫，但這種封裝方式對後續維護仍然有幫助。

---

### 5.11 `load_data(csv_path: str) -> pd.DataFrame`

**功能：**

- 讀取 CSV
- 檢查並選取必要欄位
- 補空值
- 建立 `case_document`

**為什麼要做：**
將資料前處理集中在同一個函式裡，可以避免 UI 或檢索邏輯直接操作原始資料，讓流程更乾淨。

**教學重點：**

```python
@st.cache_data
```

這個 decorator 代表：

- 讀取過的資料會被快取
- 同一路徑重跑時不用每次都重新讀檔
- 可以提升 Streamlit 操作速度

---

## 6. 程式中運用到的主要程式碼功能與教學

---

### 6.1 正規表示式 `re`

本專案用在：

- 去特殊符號
- 抽取中文區塊
- 抽取英文 token
- 標準化數字與金額

這類文字前處理在 NLP 專案非常常見。

---

### 6.2 Pandas 資料處理

用到的功能包括：

- `pd.read_csv()`：讀取 CSV
- `df[required_cols].copy()`：保留需要欄位
- `fillna("")`：補空值
- `apply(build_case_document, axis=1)`：逐列建立檢索文本
- `sort_values()`：依分數排序
- `reset_index(drop=True)`：重設索引

這些都是資料前處理的核心技巧。

---

### 6.3 TF-IDF 向量化

程式使用 `TfidfVectorizer` 將文字轉成向量。
向量化之後才能用數值方式計算「哪一筆案例最像使用者的問題」。\

優勢

- TF-IDF 是傳統、快速、可解釋的文本檢索方法
- 很適合做雛型
- 比深度模型更容易部署在本機

---

### 6.4 Cosine Similarity

`cosine_similarity()` 用於比較：

- 使用者問題向量
- 每筆案例向量

數值越高，代表兩段文字越相似。

---

### 6.5 規則式排序強化

除了機器學習向量比對，程式還加入：

- `keyword_overlap_score()`
- `solution_similarity()`

這代表系統不是單純靠模型，而是結合了：

- 統計式檢索
- 規則式過濾
- LLM 語言生成

---

### 6.6 Streamlit UI 功能

本程式使用到：

- `st.set_page_config()`：設定頁面標題與版型
- `st.title()`：顯示標題
- `st.caption()`：顯示說明
- `st.text_area()`：輸入問題
- `st.button()`：開始分析
- `st.columns()`：控制版面
- `st.empty()`：建立可更新狀態欄
- `status.info()` / `status.success()`：顯示流程進度
- `st.subheader()` / `st.write()`：顯示結果
- `st.expander()`：收納參考來源

這些寫法能讓使用者清楚知道系統是否正在運作。

---

### 6.7 API 呼叫與例外處理

使用 `requests.post()` 呼叫本地 API。
同時有錯誤處理機制，避免程式直接當掉。

---

### 6.8 OpenCC 繁簡轉換

程式中：

```python
cc = OpenCC("s2t")
```

用途是把模型可能產出的簡體字轉成繁體字。

---

## 7. 實際操作教學

### 7.1 準備檔案

請確認資料夾內至少有：

- `app.py`
- `complaints_final.csv`

---

### 7.2 啟動 Ollama

先確認 Ollama 有啟動，並已下載模型：

```bash
ollama pull qwen2.5:7b-instruct
```

若 Ollama 尚未啟動，可先開啟 Ollama 應用程式，或在某些環境下使用：

```bash
ollama serve
```

---

### 7.3 啟動 Streamlit

在 terminal 切換到 `06_app.py` 所在資料夾後執行：

```bash
python -m streamlit run 06_app.py
```

---

### 7.4 實際使用流程

1. 開啟網頁後，在文字框輸入 PM 問題
2. 按下「開始分析」
3. 系統會依序：
   - 讀取 CSV
   - 檢索相似案例
   - 組成 prompt
   - 呼叫 Ollama
   - 顯示最終回答
4. 展開「查看參考來源」，可查看對應的歷史方案與分數

---

## 8. 實際操作流程圖

### 8.1 簡易版流程圖

```text
使用者輸入問題
        ↓
Streamlit 接收輸入
        ↓
讀取 complaints_final.csv
        ↓
建立 case_document
        ↓
文字清理與斷詞
        ↓
TF-IDF 向量化
        ↓
計算 cosine similarity
        ↓
加入 keyword overlap score
        ↓
排序並過濾重複解法
        ↓
組成 Prompt
        ↓
呼叫 Ollama
        ↓
OpenCC 轉繁體
        ↓
顯示回答與參考來源
```

---

## 9. 程式特色與亮點

### 9.1 不依賴雲端 API

本專案使用本地 Ollama，不需要串接外部雲端 LLM API，較適合：

- 校內展示
- 雛型開發
- 本機測試
- 資料不方便外傳的情境

### 9.2 混合式檢索設計

不是只有用 LLM，而是先做：

- TF-IDF 相似度檢索
- 關鍵字重疊加權
- 重複解法過濾

最後才交給 LLM 生成回答。
這種方式通常比直接把問題丟給模型更穩定。

### 9.3 台灣繁體中文導向

透過：

- Prompt 限制
- OpenCC 轉換
- 台灣常用詞要求

讓輸出更符合目標使用者情境。

### 9.4 UI 具備即時狀態提示

程式使用：

- `正在讀取資料...`
- `正在檢索相似案例...`
- `正在整理回答...`

讓使用者知道系統沒有卡住，提升體驗。

---

## 10. 可能遇到的錯誤與排除方式

### 問題 1：找不到 CSV

錯誤訊息：

> 找不到 CSV 檔案，請檢查預設路徑是否正確。

**解法：**

- 確認 `complaints_final.csv` 在正確位置
- 或修改 `DEFAULT_CSV_PATH`

---

### 問題 2：無法連線到 Ollama

錯誤訊息：

> 無法連線到 Ollama。請先確認 Ollama 應用程式或 serve 服務有啟動。

**解法：**

- 確認 Ollama 有開啟
- 確認 API 位址 `http://localhost:11434/api/generate` 可用

---

### 問題 3：模型尚未下載

若模型不存在，Ollama 可能無法回覆。

**解法：**

```bash
ollama pull qwen2.5:7b-instruct
```

---

### 問題 4：回應逾時

錯誤訊息：

> Ollama 回應逾時。

**解法：**

- 增加timeout時間

---

## 13. 可延伸優化方向

未來如果要繼續優化，可以考慮：

1. 加入更多來源案例與信心分數，但是會需要人工檢查，把資料庫資料正確性提高
2. 調整為雲端和付費使用的LLM，省去因記憶體與電腦效能的限制
