"""
Laplacian 商品照片模糊分類核心功能

這個檔案只放「計算分數、建立資料夾、移動檔案、輸出報表」等核心邏輯。
Streamlit 介面放在 app.py，這樣程式結構比較清楚。
"""

from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


# 依照使用者需求：只處理 jpg / jpeg / png。
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@dataclass
class ImageResult:
    """儲存單張圖片的處理結果，最後會輸出成 CSV 報表。"""

    filename: str
    source_path: str
    destination_path: str
    score: float | None
    result: str
    reason: str


def sanitize_folder_name(name: str) -> str:
    """
    將店家名稱轉成安全的資料夾名稱。

    Windows 資料夾不能使用這些符號：\\ / : * ? " < > |
    另外也移除前後空白，避免資料夾名稱看起來一樣但實際不同。
    """

    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "未命名店家"


def create_run_folders(output_parent: Path, store_name: str, run_date: date) -> tuple[Path, Path, Path]:
    """
    建立本次執行的結果資料夾。

    資料夾格式：店家名稱_年月日
    例如：小王寵物店_20260505

    如果同一天、同店家已經執行過，為了避免覆蓋舊結果，會自動加流水號：
    小王寵物店_20260505_02
    小王寵物店_20260505_03
    """

    output_parent = Path(output_parent)
    output_parent.mkdir(parents=True, exist_ok=True)

    safe_store_name = sanitize_folder_name(store_name)
    date_text = run_date.strftime("%Y%m%d")
    base_dir = output_parent / f"{safe_store_name}_{date_text}"

    run_dir = base_dir
    counter = 2
    while run_dir.exists():
        run_dir = output_parent / f"{safe_store_name}_{date_text}_{counter:02d}"
        counter += 1

    ok_dir = run_dir / "ok"
    fail_dir = run_dir / "fail"
    ok_dir.mkdir(parents=True, exist_ok=True)
    fail_dir.mkdir(parents=True, exist_ok=True)

    return run_dir, ok_dir, fail_dir


def iter_supported_images(input_dir: Path) -> Iterable[Path]:
    """只列出來源資料夾第一層的 jpg / jpeg / png 圖片。"""

    input_dir = Path(input_dir)
    for path in sorted(input_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            yield path


def iter_unsupported_files(input_dir: Path) -> Iterable[Path]:
    """
    列出非 jpg / jpeg / png 的檔案。

    這些檔案不會被移動，避免把 Excel、PDF、文字檔等資料誤搬到 fail。
    """

    input_dir = Path(input_dir)
    for path in sorted(input_dir.iterdir()):
        if path.is_file() and path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            yield path


def read_image(path: Path) -> np.ndarray | None:
    """
    讀取圖片，讀不到就回傳 None。

    這裡用 np.fromfile + cv2.imdecode，對中文路徑比較穩定。
    """

    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None


def variance_of_laplacian(image: np.ndarray) -> float:
    """
    計算 Laplacian variance，也就是照片清晰度分數。

    分數越高：通常代表邊緣越清楚、照片越不模糊。
    分數越低：通常代表邊緣資訊少、照片越模糊。
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def make_unique_destination(destination: Path) -> Path:
    """
    避免覆蓋同名檔案。

    例如 fail 資料夾已經有 A.jpg，新的 A.jpg 會改成 A_001.jpg。
    """

    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter:03d}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_file(
    source: Path,
    destination_dir: Path,
) -> Path:
    """
    移動檔案到指定資料夾。

    這裡是直接移動，不是複製，
    所以不會額外占用一份照片空間。

    因為每次執行都會建立新的結果資料夾，
    所以一般情況下不會有同名檔案覆蓋問題。
    """

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = destination_dir / source.name

    shutil.move(
        str(source),
        str(destination),
    )

    return destination


def classify_single_image(image_path: Path, threshold: float, ok_dir: Path, fail_dir: Path) -> ImageResult:
    """
    處理單張圖片。

    1. 嘗試讀取圖片
    2. 如果讀不到，直接移到 fail
    3. 如果讀得到，計算 Laplacian 分數
    4. 分數 >= threshold 移到 ok；分數 < threshold 移到 fail
    """

    image = read_image(image_path)

    if image is None:
        destination = move_file(image_path, fail_dir)
        return ImageResult(
            filename=image_path.name,
            source_path=str(image_path),
            destination_path=str(destination),
            score=None,
            result="fail",
            reason="圖片讀取失敗，已移到 fail",
        )

    score = variance_of_laplacian(image)

    if score >= threshold:
        destination = move_file(image_path, ok_dir)
        return ImageResult(
            filename=image_path.name,
            source_path=str(image_path),
            destination_path=str(destination),
            score=score,
            result="ok",
            reason=f"清晰度分數 {score:.2f} >= 標準 {threshold:.0f}",
        )

    destination = move_file(image_path, fail_dir)
    return ImageResult(
        filename=image_path.name,
        source_path=str(image_path),
        destination_path=str(destination),
        score=score,
        result="fail",
        reason=f"清晰度分數 {score:.2f} < 標準 {threshold:.0f}",
    )


def write_report_csv(results: list[ImageResult], report_path: Path) -> None:
    """將結果輸出成 CSV，使用 utf-8-sig，Excel 開啟中文比較不會亂碼。"""

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "source_path",
                "destination_path",
                "score",
                "result",
                "reason",
            ],
        )
        writer.writeheader()

        for item in results:
            writer.writerow(
                {
                    "檔案名稱": item.filename,
                    "原始路徑": item.source_path,
                    "移動路徑": item.destination_path,
                    "分數": "" if item.score is None else f"{item.score:.4f}",
                    "結果": item.result,
                    "原因": item.reason,
                }
            )
