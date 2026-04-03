from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta
from database import init_db, get_connection
from models import NippouCreate, NippouResponse

app = FastAPI()

init_db()

@app.post("/nippou", response_model=NippouResponse)
def create_nippou(body: NippouCreate):
    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST).isoformat()

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO daily_reports
            (date, timeblock, theme, details, tomorrow, note,
            created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (body.date, body.timeblock, body.theme, body.details,
            body.tomorrow, body.note, now, now)
        )
        conn.commit()
    except Exception:
        raise HTTPException(status_code=400,
detail="同じ日付の日報がすでに存在します")
    finally:
        conn.close()

    return {**body.model_dump(), "created_at": now, "updated_at": now}


@app.get("/nippou", response_model=list[NippouResponse])
def get_nippou_list():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM daily_reports ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/nippou/{date}", response_model=NippouResponse)
def get_nippou_by_date(date: str):
    try:
        conn = get_connection()
        row = conn.execute("SELECT * FROM daily_reports WHERE date = ?", (date, )).fetchone()
    except Exception:
        raise HTTPException(status_code=500, detail="日報が見つかりません。")
    
    if row is None:
        raise HTTPException(status_code=400, detail="日報が見つかりません。")
    conn.close()
    return dict(row)

@app.put("/nippou/{date}", response_model=NippouResponse)
def put_nippou(date: str, body: NippouCreate):
    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST).isoformat()

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE daily_reports SET
            timeblock = ?,
            theme = ?,
            details = ?,
            tomorrow = ?,
            note = ?,
            updated_at = ?
            WHERE date = ?
            """,
        (body.timeblock, body.theme, body.details,
            body.tomorrow, body.note, now, date))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="日報が見つかりません")
        conn.commit()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="更新エラー")
    finally:
        conn.close()

    row = get_connection().execute(
        "SELECT * FROM daily_reports WHERE date = ?", (date,)
    ).fetchone()
    return dict(row)