# FastAPI エンドポイントの統合テスト
# テスト用DBとして /tmp/test_nippou.db を使用し、本番DBには影響しない

# --- 標準ライブラリ ---
import os
import time

# --- サードパーティ ---
import pytest
from fastapi.testclient import TestClient

# --- ローカル ---
import database
database.DB_PATH = "/tmp/test_nippou.db"  # main より前に設定する必要がある
from main import app
database.init_db()
import excel
from excel import delete_sheet_excel


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """各テストの前にDBを初期化して、テスト間のデータ混入を防ぐ"""
    if os.path.exists(database.DB_PATH):
        os.remove(database.DB_PATH)
    database.init_db()


# テストデータ
sample_report = {
    "date": "2026-02-29",  # 閏年の日付（Excelに既存シートがない日付を使用）
    "timeblock": "9:00-18:00",
    "theme": "テスト",
    "details": "詳細",
    "tomorrow": "明日のテーマ",
}

another_report = {
    "date": "2026-04-04",
    "timeblock": "9:00-18:00",
    "theme": "テスト2",
    "details": "詳細2",
    "tomorrow": "明日のテーマ2"
}


# --- 正常系 ---

def test_create_report_succeeds():
    """POST /nippou: 正常なデータで日報を作成できる"""
    response = client.post("/nippou", json=sample_report)
    assert response.status_code == 200

    data = response.json()
    for key in sample_report:
        assert data[key] == sample_report[key]


def test_list_reports_returns_empty_when_no_data():
    """GET /nippou: データが0件のとき空リストが返る"""
    response = client.get("/nippou")
    assert response.json() == []


def test_list_reports_returns_all_records():
    """GET /nippou: 複数件登録後、全件が返る"""
    client.post("/nippou", json=sample_report)
    client.post("/nippou", json=another_report)

    response = client.get("/nippou")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_report_by_date_returns_correct_data():
    """GET /nippou/{date}: 指定した日付の日報が取得できる"""
    client.post("/nippou", json=sample_report)
    response = client.get(f"/nippou/{sample_report['date']}")
    assert response.status_code == 200

    data = response.json()
    for key in sample_report:
        assert data[key] == sample_report[key]


def test_update_report_succeeds():
    """PUT /nippou/{date}: 既存の日報を更新できる"""
    client.post("/nippou", json=sample_report)
    updated_data = {**sample_report, "theme": "更新後テーマ"}

    response = client.put(f"/nippou/{sample_report['date']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["theme"] == "更新後テーマ"


def test_update_report_updates_timestamp():
    """PUT /nippou/{date}: 更新後にupdated_atがcreated_atより新しくなる"""
    client.post("/nippou", json=sample_report)
    # created_at と updated_at に時間差を作るために1秒待つ
    time.sleep(1)
    response = client.put(f"/nippou/{sample_report['date']}", json=sample_report)
    assert response.json()["updated_at"] != response.json()["created_at"]


def test_export_nippou():
    """POST /nippou/{date}/export: Excelファイルに日報を書き込める"""
    client.post("/nippou", json=sample_report)
    response = client.post(f"/nippou/{sample_report['date']}/export")
    try:
        assert response.status_code == 200
    finally:
        delete_sheet_excel(sample_report["date"])


# --- 異常系 ---

def test_create_report_fails_on_duplicate_date():
    """POST /nippou: 同じ日付で2回登録すると400が返る"""
    client.post("/nippou", json=sample_report)
    response = client.post("/nippou", json=sample_report)
    assert response.status_code == 400


def test_get_report_returns_error_for_nonexistent_date():
    """GET /nippou/{date}: 存在しない日付を指定すると400が返る"""
    response = client.get("/nippou/9999-99-99")
    assert response.status_code == 400


def test_nonexistent_endpoint_returns_404():
    """存在しないエンドポイントにアクセスすると404が返る"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_update_report_fails_for_nonexistent_date():
    """PUT /nippou/{date}: 存在しない日付を指定すると404が返る"""
    response = client.put("/nippou/9999-99-99", json=sample_report)
    assert response.status_code == 404


def test_export_fails_for_nonexistent_date():
    """POST /nippou/{date}/export: 存在しない日付を指定すると404が返る"""
    response = client.post("/nippou/9999-99-99/export")
    assert response.status_code == 404


def test_export_fails_when_file_not_found():
    """POST /nippou/{date}/export: Excelファイルが存在しないとき500が返る"""
    original = excel.EXCEL_PATH
    excel.EXCEL_PATH = "/tmp/nonexistent.xlsx"

    client.post("/nippou", json=sample_report)
    response = client.post(f"/nippou/{sample_report['date']}/export")
    try:
        assert response.status_code == 500
    finally:
        excel.EXCEL_PATH = original
