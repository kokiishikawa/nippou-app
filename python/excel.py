import openpyxl
import os
from dotenv import load_dotenv

load_dotenv()

EXCEL_PATH = os.environ['EXCEL_PATH']
TEMPLATE_SHEET = "テンプレート"

def export_to_excel(report: dict):
    
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Excelファイルが見つかりません：{EXCEL_PATH}")

    wb = openpyxl.load_workbook(EXCEL_PATH)

    template = wb[TEMPLATE_SHEET]
    new_sheet = wb.copy_worksheet(template)
    new_sheet.title = report["date"]

    new_sheet["K2"] = report["date"]
    new_sheet["A4"] = report["timeblock"]
    new_sheet["A10"] = report["theme"]
    new_sheet["A13"] = report["details"]
    new_sheet["A47"] = report["tomorrow"]
    if report.get("note"):
        new_sheet["A52"] = report["note"]

    wb.save(EXCEL_PATH)

def delete_sheet_excel(date: str) -> str:
    """書き込みテスト後にシートを削除する用"""
    wb = openpyxl.load_workbook(EXCEL_PATH)
    wb.remove(wb[date])
    wb.save(EXCEL_PATH)

# if __name__ == "__main__":
#     delete_sheet_excel()