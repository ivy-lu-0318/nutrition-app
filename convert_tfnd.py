"""
TFND Excel → tfnd.json 轉換腳本
使用方式：
  1. 從 https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178 下載 Excel 檔案
  2. 把 Excel 檔案放在這個腳本同目錄下，命名為 TFND.xlsx
  3. 執行：python convert_tfnd.py
  4. 產出 tfnd.json
"""

import json
import sys
import pandas as pd

EXCEL_FILE = "TFND.xlsx"

# TFND 常見欄位名稱對應（不同版本可能不同，若失敗會列出實際欄位供你對照）
COLUMN_MAP_CANDIDATES = [
    {
        "name": "樣品名稱",
        "calories": "熱量",
        "protein": "粗蛋白",
        "carbs": "總碳水化合物",
        "fat": "粗脂肪",
    },
    {
        "name": "食品名稱",
        "calories": "熱量(kcal)",
        "protein": "蛋白質(g)",
        "carbs": "碳水化合物(g)",
        "fat": "脂肪(g)",
    },
    {
        "name": "樣品名稱",
        "calories": "熱量(kcal)",
        "protein": "蛋白質",
        "carbs": "碳水化合物",
        "fat": "脂肪",
    },
]

def find_columns(df):
    for mapping in COLUMN_MAP_CANDIDATES:
        if all(col in df.columns for col in mapping.values()):
            return mapping
    return None

def convert():
    try:
        df = pd.read_excel(EXCEL_FILE, skiprows=0)
    except FileNotFoundError:
        print(f"找不到 {EXCEL_FILE}，請確認檔案放在同目錄下")
        sys.exit(1)

    mapping = find_columns(df)
    if mapping is None:
        print("❌ 找不到對應欄位，請對照下方實際欄位名稱，修改腳本的 COLUMN_MAP_CANDIDATES：")
        print(list(df.columns))
        sys.exit(1)

    foods = []
    for _, row in df.iterrows():
        name = str(row[mapping["name"]]).strip()
        if not name or name == "nan":
            continue

        def to_float(val):
            try:
                return round(float(val), 2)
            except (ValueError, TypeError):
                return 0.0

        foods.append({
            "id": f"tfnd_{len(foods)}",
            "name": name,
            "source": "tfnd",
            "per100g": {
                "calories": to_float(row[mapping["calories"]]),
                "protein":  to_float(row[mapping["protein"]]),
                "carbs":    to_float(row[mapping["carbs"]]),
                "fat":      to_float(row[mapping["fat"]]),
            }
        })

    with open("tfnd.json", "w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！共匯入 {len(foods)} 筆食物資料 → tfnd.json")

if __name__ == "__main__":
    convert()
