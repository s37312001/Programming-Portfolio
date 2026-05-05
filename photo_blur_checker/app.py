"""
兩種執行方式：
1. 在資料夾內直接點擊 run_app.bat 打開 Streamlit。
2. 若瀏覽按鈕因環境限制無法開啟，手動貼上資料夾路徑。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from blur_core import (
    ImageResult,
    classify_single_image,
    create_run_folders,
    iter_supported_images,
    iter_unsupported_files,
    write_report_csv,
)


# -----------------------------
# Streamlit 畫面設定
# -----------------------------

st.set_page_config(
    page_title="Laplacian應用:商品照片模糊比對小工具",
    page_icon="📷",
    layout="wide",
)


# -----------------------------
# 小工具函式
# -----------------------------


def choose_folder_dialog() -> str:
    """
    開啟本機資料夾選擇視窗。

    如果這個 Streamlit 是在自己的電腦執行，按鈕會在自己的電腦跳出資料夾選擇視窗。
    如果 Streamlit 是部署在雲端或別台電腦，資料夾視窗不一定會出現在自己的畫面上。
    若按鈕沒有反應，請直接手動貼上資料夾路徑。
    """

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory()
        root.destroy()
        return folder or ""
    except Exception:
        return ""


def threshold_description(threshold: int) -> str:
    """把數字 threshold 轉成一般人比較好懂的文字說明。"""

    if threshold <= 300:
        return "很寬鬆：只有非常模糊的照片才會進 fail。"
    if threshold <= 600:
        return "偏寬鬆：適合先快速抓出明顯模糊的照片。"
    if threshold <= 800:
        return "一般建議：適合商品照初步篩選。"
    if threshold <= 1100:
        return "偏嚴格：照片需要有比較清楚的文字、邊緣或紋理。"
    return "非常嚴格：很多稍微不清楚的照片都可能會進 fail。"


def results_to_dataframe(results: list[ImageResult]) -> pd.DataFrame:
    """將處理結果轉成 Streamlit 可以顯示的表格。"""

    rows = []

    for item in results:
        rows.append(
            {
                "檔名": item.filename,
                "結果": item.result,
                "Laplacian 分數": None if item.score is None else round(item.score, 2),
                "原因": item.reason,
                "移動後位置": item.destination_path,
            }
        )

    return pd.DataFrame(rows)


# -----------------------------
# 初始化 session_state
# -----------------------------

if "input_dir" not in st.session_state:
    st.session_state.input_dir = ""

if "output_parent" not in st.session_state:
    st.session_state.output_parent = ""

if "folder_dialog_message" not in st.session_state:
    st.session_state.folder_dialog_message = ""


def choose_input_folder() -> None:
    """
    按下「瀏覽來源資料夾」時執行。

    這個函式會：
    1. 打開資料夾選擇視窗
    2. 把使用者選到的資料夾路徑，放進 input_dir 輸入框

    因為 Streamlit 不建議在輸入框建立後，馬上直接修改它的值，
    所以用 on_click 可以讓 Streamlit 先更新路徑，再重新整理畫面，比較不會報錯。
    """

    selected = choose_folder_dialog()

    if selected:
        st.session_state.input_dir = selected
        st.session_state.folder_dialog_message = ""
    else:
        st.session_state.folder_dialog_message = (
            "無法開啟來源資料夾選擇視窗，請直接貼上資料夾路徑。"
        )


def choose_output_folder() -> None:
    """按下「瀏覽存放位置」時執行。"""

    selected = choose_folder_dialog()

    if selected:
        st.session_state.output_parent = selected
        st.session_state.folder_dialog_message = ""
    else:
        st.session_state.folder_dialog_message = (
            "無法開啟結果存放位置選擇視窗，請直接貼上資料夾路徑。"
        )


# -----------------------------
# 主畫面
# -----------------------------

st.title("📷 Laplacian應用:商品照片模糊比對小工具")

st.write(
    "把商品照片放在同一個資料夾後，這個工具會計算每張照片的清晰度分數，"
    "並直接把照片移動到 `ok` 或 `fail` 資料夾。"
)

with st.expander("使用前提醒", expanded=True):
    st.markdown(
        """
- 目前只處理 `.jpg`、`.jpeg`、`.png`。
- 這個版本會**直接移動照片**，不是複製，所以來源資料夾內的圖片會被搬走。
- 若圖片副檔名是 jpg / jpeg / png，但檔案壞掉或 OpenCV 讀不到，會直接移到 `fail`。
- 非 jpg / jpeg / png 的檔案不會被移動，避免誤搬 Excel、PDF、文字檔。
- 每次執行都會建立一個新的結果資料夾，格式為：`店家名稱_年月日`。
        """
    )

left_col, right_col = st.columns(2)

with left_col:
    store_name = st.text_input(
        "店家名稱",
        placeholder="例如：竹君烘焙房",
    )

    run_date = st.date_input(
        "日期",
        value=date.today(),
    )

with right_col:
    threshold = st.slider(
        "模糊判斷標準（往右越嚴格）",
        min_value=100,
        max_value=1500,
        value=700,
        step=50,
        help="照片的 Laplacian 分數低於這個標準會進 fail；高於或等於這個標準會進 ok。",
    )

    st.info(threshold_description(threshold))

    st.caption(
        "判斷方式：Laplacian 分數越低通常越模糊；"
        "標準拉越高，代表越嚴格，進 fail 的照片會變多。"
    )


# -----------------------------
# 來源資料夾
# -----------------------------

st.subheader("1. 選擇來源照片資料夾")

folder_col_1, folder_col_2 = st.columns([4, 1])

with folder_col_1:
    st.text_input(
        "來源照片資料夾路徑",
        key="input_dir",
        placeholder=r"例如：C:\Users\Joy\Downloads\商品照片",
    )

with folder_col_2:
    st.write("")
    st.write("")
    st.button(
        "瀏覽來源資料夾",
        on_click=choose_input_folder,
    )


# -----------------------------
# 結果存放位置
# -----------------------------

st.subheader("2. 選擇結果存放位置")

output_col_1, output_col_2 = st.columns([4, 1])

with output_col_1:
    st.text_input(
        "結果要存放在哪個資料夾底下",
        key="output_parent",
        placeholder=r"例如：C:\Users\Joy\Downloads\分類結果",
    )

with output_col_2:
    st.write("")
    st.write("")
    st.button(
        "瀏覽存放位置",
        on_click=choose_output_folder,
    )


if st.session_state.folder_dialog_message:
    st.warning(st.session_state.folder_dialog_message)


# -----------------------------
# 執行前檢查
# -----------------------------

st.subheader("3. 開始分類")

input_dir = Path(st.session_state.input_dir) if st.session_state.input_dir else None
output_parent = Path(st.session_state.output_parent) if st.session_state.output_parent else None

can_run = True

if not store_name.strip():
    can_run = False
    st.warning("請先輸入店家名稱。")

if input_dir is None or not input_dir.exists() or not input_dir.is_dir():
    can_run = False
    st.warning("請選擇或輸入有效的來源照片資料夾。")

if output_parent is None:
    can_run = False
    st.warning("請選擇或輸入結果存放位置。")


# -----------------------------
# 顯示來源資料夾資訊
# -----------------------------

if input_dir and input_dir.exists() and input_dir.is_dir():
    supported_files = list(iter_supported_images(input_dir))
    unsupported_files = list(iter_unsupported_files(input_dir))

    metric_col_1, metric_col_2 = st.columns(2)

    metric_col_1.metric(
        "可處理圖片數",
        len(supported_files),
    )

    metric_col_2.metric(
        "略過的非 jpg/jpeg/png 檔案數(不會被移動)",
        len(unsupported_files),
    )

    if unsupported_files:
        with st.expander("查看略過的檔案名稱"):
            st.write([p.name for p in unsupported_files])

    if not supported_files:
        can_run = False
        st.warning("來源資料夾裡沒有可處理的 jpg / jpeg / png 圖片。")


# -----------------------------
# 開始分類
# -----------------------------

start = st.button(
    "開始移動並分類照片",
    type="primary",
    disabled=not can_run,
)

if start:
    assert input_dir is not None
    assert output_parent is not None

    supported_files = list(iter_supported_images(input_dir))

    run_dir, ok_dir, fail_dir = create_run_folders(
        output_parent=output_parent,
        store_name=store_name,
        run_date=run_date,
    )

    results: list[ImageResult] = []

    progress = st.progress(0)
    status_text = st.empty()

    for index, image_path in enumerate(supported_files, start=1):
        status_text.write(
            f"處理中：{image_path.name} ({index}/{len(supported_files)})"
        )

        result = classify_single_image(
            image_path=image_path,
            threshold=float(threshold),
            ok_dir=ok_dir,
            fail_dir=fail_dir,
        )

        results.append(result)

        progress.progress(index / len(supported_files))

    report_path = run_dir / "classification_report.csv"

    write_report_csv(
        results=results,
        report_path=report_path,
    )

    df = results_to_dataframe(results)

    ok_count = int((df["結果"] == "ok").sum()) if not df.empty else 0
    fail_count = int((df["結果"] == "fail").sum()) if not df.empty else 0

    st.success("分類完成！")

    st.write(f"結果資料夾：`{run_dir}`")
    st.write(f"報表位置：`{report_path}`")

    summary_col_1, summary_col_2, summary_col_3 = st.columns(3)

    summary_col_1.metric("ok 張數", ok_count)
    summary_col_2.metric("fail 張數", fail_count)
    summary_col_3.metric("總處理張數", len(results))

    st.dataframe(
        df,
        use_container_width=True,
    )

    with report_path.open("rb") as f:
        st.download_button(
            label="下載 CSV 報表",
            data=f,
            file_name="classification_report.csv",
            mime="text/csv",
        )