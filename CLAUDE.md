@AGENTS.md

# CLAUDE.md

## 私について

- 実務経験なし、学習中のエンジニア
- コードは自分でも理解・実装したいので、全部やってしまわないこと
- 実装は 4 割程度の支援が理想

## Claude への指示

- コードを書く前に「何をするか・なぜそうするか」を必ず説明する
- 一度に全部実装しない、ステップごとに分けて提示する
- 既存コードを変更する前に必ず確認を取る
- わからないことは推測で進めず質問する
- 実装後に「ここは自分で試してみて」という箇所を示す

## コマンド

```bash
npm run dev       # 開発サーバー起動 (http://localhost:3000)
npm run build     # 本番用ビルド
npm run start     # 本番サーバー起動
npm run lint      # ESLint 実行
npx tsc --noEmit  # 型チェック

# FastAPI
cd python && uvicorn main:app --reload --port 8000
```

## アーキテクチャ

研修日報の作成・管理・Excel出力を行うWebアプリ。
別途作成している /nippou スキルからAPIで自動書き込みもできる。

### 技術スタック

| 役割 | 技術 | 理由 |
|------|------|------|
| フロントエンド | Next.js (App Router) + TypeScript |  |
| バックエンド | Next.js API Routes | シンプルにフルスタック構成 |
| Excel書き込み | FastAPI (Python) + openpyxl | Python資産を活かす |
| DB | SQLite (ローカル) → PostgreSQL (AWS移行時) | ローカルは設定ゼロ |
| DBアクセス | node:sqlite (Node.js 22 組み込み) | 外部パッケージ不要 |

### データモデル

```sql
CREATE TABLE daily_reports (
  date       TEXT PRIMARY KEY,  -- 例: "2026-04-02"
  timeblock  TEXT NOT NULL,
  theme      TEXT NOT NULL,
  details    TEXT NOT NULL,
  tomorrow   TEXT NOT NULL,
  note       TEXT,              -- 備考（任意）
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### API仕様

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/nippou` | 日報作成 |
| GET | `/api/nippou` | 一覧取得 |
| GET | `/api/nippou/:date` | 特定日取得 |
| PUT | `/api/nippou/:date` | 更新 |
| POST | `/api/nippou/:date/export` | Excel出力 |

### 画面構成

```
/               # 日報一覧（カレンダー or リスト）
/[date]         # 日報詳細・編集
/[date]/export  # Excel出力プレビュー
```

### ディレクトリ構成

```
nippou-app/
├── app/
│   ├── page.tsx                          # 日報一覧
│   ├── [date]/
│   │   ├── page.tsx                      # 詳細・編集
│   │   └── export/page.tsx               # Excel出力プレビュー
│   └── api/nippou/
│       ├── route.ts                      # GET(一覧), POST(作成)
│       └── [date]/
│           ├── route.ts                  # GET, PUT
│           └── export/route.ts           # POST(Excel出力)
├── lib/
│   └── db.ts                             # DB接続・初期化
├── python/                               # FastAPI + openpyxl
│   ├── main.py
│   └── requirements.txt
└── CLAUDE.md
```

### 注意事項

- Node.js は v22 LTS を使用（`node:sqlite` が使える最低ラインは v22.5）
- DBはローカルでは SQLite（`node:sqlite` で直接アクセス）、AWS移行時は PostgreSQL に切り替え
- Excel出力は FastAPI 側で処理し、Next.js API Routes から HTTP で呼び出す

## 開発フェーズ

| Phase | 内容 | 状態 |
|-------|------|------|
| 1 | DB設計・API実装（CRUD） | 未着手 |
| 2 | フロントエンド実装（一覧・詳細・編集） | 未着手 |
| 3 | FastAPI + Excel出力機能 | 未着手 |
| 4 | /nippou スキルとの連携確認 | 未着手 |
| 5 | AWS移行（余裕があれば） | 未着手 |
