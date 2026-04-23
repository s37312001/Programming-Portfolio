import re
from typing import List

import pandas as pd
import requests
import streamlit as st
from opencc import OpenCC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# 基本設定
# =========================
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b-instruct"
DEFAULT_CSV_PATH = "complaints_final.csv"  # 改成你的預設 CSV 路徑

cc = OpenCC("s2t")

st.set_page_config(
    page_title="PM小幫手",
    page_icon="🤖",
    layout="wide"
)

# =========================
# 文字前處理
# =========================
stopwords = {
    "的", "了", "呢", "嗎", "我", "想", "請問", "一下", "如何", "怎麼", "要", "該", "是不是",
    "a", "an", "the", "is", "are", "to", "for", "and", "or", "in", "on", "with"
}


def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\u4e00-\u9fff\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> List[str]:
    text = normalize_text(text)

    zh_blocks = re.findall(r"[\u4e00-\u9fff]+", text)
    en_tokens = re.findall(r"[a-zA-Z0-9_]+", text)

    zh_tokens = []
    for block in zh_blocks:
        block = block.strip()
        if len(block) == 1:
            zh_tokens.append(block)
        else:
            for n in [2, 3, 4]:
                for i in range(len(block) - n + 1):
                    zh_tokens.append(block[i:i + n])

    all_tokens = zh_tokens + en_tokens
    return [t for t in all_tokens if t not in stopwords and len(t) > 1]


def normalize_solution_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"\$[\d,]+(\.\d+)?", "金額", text)
    text = re.sub(r"\d+(\.\d+)?", "數字", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def solution_similarity(sol1: str, sol2: str) -> float:
    tokens1 = set(tokenize(normalize_solution_text(sol1)))
    tokens2 = set(tokenize(normalize_solution_text(sol2)))

    if not tokens1 or not tokens2:
        return 0.0

    return len(tokens1 & tokens2) / max(len(tokens1), 1)


def keyword_overlap_score(question: str, case_doc: str) -> float:
    q_tokens = set(tokenize(question))
    c_tokens = set(tokenize(case_doc))

    if not q_tokens or not c_tokens:
        return 0.0

    return len(q_tokens & c_tokens) / max(len(q_tokens), 1)


# =========================
# 建立檢索文本
# =========================
def build_case_document(row: pd.Series) -> str:
    parts = [
        str(row.get("Issue", "")),
        str(row.get("Sub-issue", "")),
        str(row.get("Consumer complaint narrative in Chinese", "")),
        str(row.get("Consumer complaint narrative in Chinese", "")),
        str(row.get("Solution in Chinese", "")),
        str(row.get("Solution in Chinese", ""))
    ]
    return "\n".join([p for p in parts if p.strip() != ""])


# =========================
# Retrieval：不使用 find_best_category()
# =========================
def rank_cases(question: str, df: pd.DataFrame, top_k: int = 3) -> pd.DataFrame:
    if "case_document" not in df.columns:
        raise ValueError("df 裡沒有 case_document 欄位，請先建立它。")

    filtered_df = df.copy()

    docs = filtered_df["case_document"].tolist()
    corpus = docs + [question]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        min_df=1
    )
    matrix = vectorizer.fit_transform(corpus)

    case_vectors = matrix[:-1]
    question_vector = matrix[-1]
    similarities = cosine_similarity(question_vector, case_vectors).flatten()

    rows = []
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        sim = float(similarities[i])
        keyword_score = keyword_overlap_score(question, row["case_document"])
        final_score = (sim * 0.7) + (keyword_score * 0.3)

        rows.append({
            "Complaint ID": row.get("Complaint ID", ""),
            "Issue": row.get("Issue", ""),
            "Sub-issue": row.get("Sub-issue", ""),
            "Consumer complaint narrative in Chinese": row.get("Consumer complaint narrative in Chinese", ""),
            "Solution in Chinese": row.get("Solution in Chinese", ""),
            "similarity_score": sim,
            "keyword_score": keyword_score,
            "final_score": final_score
        })

    result_df = pd.DataFrame(rows).sort_values("final_score", ascending=False).reset_index(drop=True)

    unique_solutions = []
    for _, row in result_df.iterrows():
        current_solution = row["Solution in Chinese"]

        is_similar = False
        for saved_row in unique_solutions:
            sim_score = solution_similarity(current_solution, saved_row["Solution in Chinese"])
            if sim_score > 0.75:
                is_similar = True
                break

        if not is_similar:
            unique_solutions.append(row)

        if len(unique_solutions) >= top_k:
            break

    return pd.DataFrame(unique_solutions).reset_index(drop=True)


# =========================
# Prompt
# =========================
def build_prompt(question: str, top_results: pd.DataFrame) -> str:
    solution_blocks = []

    for i, row in top_results.iterrows():
        solution = str(row["Solution in Chinese"]).replace("建議處理方案（專業版）：", "").strip()
        solution_blocks.append(f"方案{i+1}：{solution}")

    solutions_text = "\n\n".join(solution_blocks)

    prompt = f"""
請只使用繁體中文回答，禁止使用任何簡體字。

你是台灣公司內部的資深 PM 助手，要幫一位沒有經驗的新手 PM 判斷問題。

使用者問題：
{question}

系統找到的參考方案：
{solutions_text}

請你根據上面的方案，整理成自然、白話、像真人主管帶新人的回答。

規則：
1. 先用 2 句話理解問題。
2. 再整理成 3 個排查方向。
3. 每個方向要講清楚先做什麼。
4. 只採用與問題主題一致的方案。
5. 如果某個方案明顯屬於別的題型，請直接忽略，不要寫進回答。
6. 若高相關方向不足三個，寧可只回答兩個，也不要硬湊不相關內容。
7. 不要逐字抄原文，但要保留具體動作與關鍵詞，例如付款 ID、trace number、入帳紀錄、清算結果、沖回、補件、風控、合規、解除限制、返還餘額。
8. 請使用台灣常用繁體中文詞彙，例如「帳戶、後台、聯絡、資料、流程」，不要使用「賬戶、後臺、聯繫」這類中國用語。
9. 請避免過度空泛或教科書式回答，要像主管直接告訴新人下一步怎麼做。

最後請明確告訴我：第一步先查什麼，原因是什麼。
"""
    return prompt.strip()


# =========================
# Ollama
# =========================
def ask_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "system": "你是台灣的資深產品經理助理。你必須只使用繁體中文回答，禁止使用任何簡體字。",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        result = data.get("response", "").strip()
        result = cc.convert(result)
        return result

    except requests.exceptions.ConnectionError:
        return "無法連線到 Ollama。請先確認 Ollama 應用程式或 serve 服務有啟動。"
    except requests.exceptions.Timeout:
        return "Ollama 回應逾時。"
    except requests.exceptions.HTTPError:
        return f"Ollama HTTP 錯誤：{response.text}"
    except Exception as e:
        return f"Ollama 呼叫失敗：{e}"


def pm_ai_assistant(question: str, df: pd.DataFrame, top_k: int = 3):
    top_results = rank_cases(question, df, top_k=top_k)
    prompt = build_prompt(question, top_results)
    answer = ask_ollama(prompt)
    return answer, top_results


# =========================
# 讀取 CSV
# =========================
@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required_cols = [
        "Complaint ID",
        "Issue",
        "Sub-issue",
        "Consumer complaint narrative",
        "Consumer complaint narrative in Chinese",
        "Solution in Chinese"
    ]
    df = df[required_cols].copy()
    df = df.fillna("")
    df["case_document"] = df.apply(build_case_document, axis=1)
    return df


# =========================
# UI
# =========================
st.title("🤖 PM小幫手")
st.caption("輸入問題後，系統會根據既有客訴案例與處理方式，整理出自然語言建議。")

csv_path = DEFAULT_CSV_PATH

question = st.text_area(
    "請輸入你的問題",
    placeholder="例如：消費者反映付款後沒有收到正確結果，該怎麼排查？",
    height=100
)

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("開始分析", use_container_width=True)

if run_btn:
    if not question.strip():
        st.error("請先輸入問題。")
    else:
        status = st.empty()

        try:
            status.info("正在讀取資料...")
            df = load_data(csv_path.strip())

            status.info("正在檢索相似案例...")
            top_results = rank_cases(question, df, top_k=3)

            status.info("正在整理回答...")
            prompt = build_prompt(question, top_results)
            answer = ask_ollama(prompt)

            status.success("分析完成")

            st.subheader("小幫手回覆")
            st.write(answer)

            with st.expander("查看參考來源"):
                for i, row in top_results.iterrows():
                    solution = str(row["Solution in Chinese"]).replace("建議處理方案（專業版）：", "").strip()
                    st.markdown(f"### 來源 {i+1}")
                    st.write(solution)
                    st.caption(
                        f"Issue: {row['Issue']} | Sub-issue: {row['Sub-issue']} | "
                        f"score={row['final_score']:.4f}"
                    )

        except FileNotFoundError:
            status.empty()
            st.error("找不到 CSV 檔案，請檢查預設路徑是否正確。")
        except Exception as e:
            status.empty()
            st.error(f"執行時發生錯誤：{e}")