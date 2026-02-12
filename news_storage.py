import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_history.db")
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_history.json")

_initialized = False


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_db():
    global _initialized
    if _initialized:
        return
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_key TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT,
            published TEXT,
            summary TEXT,
            full_content TEXT,
            source TEXT,
            image_url TEXT,
            sentiment TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(company_key, title)
        );

        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_news_company_key ON news(company_key);
        CREATE INDEX IF NOT EXISTS idx_news_published ON news(published);
    """)

    # Check if FTS table exists
    fts_exists = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='news_fts'"
    ).fetchone()

    if not fts_exists:
        cursor.executescript("""
            CREATE VIRTUAL TABLE news_fts USING fts5(
                title,
                full_content,
                summary,
                content='news',
                content_rowid='id'
            );

            CREATE TRIGGER IF NOT EXISTS news_ai AFTER INSERT ON news BEGIN
                INSERT INTO news_fts(rowid, title, full_content, summary)
                VALUES (new.id, new.title, new.full_content, new.summary);
            END;

            CREATE TRIGGER IF NOT EXISTS news_ad AFTER DELETE ON news BEGIN
                INSERT INTO news_fts(news_fts, rowid, title, full_content, summary)
                VALUES ('delete', old.id, old.title, old.full_content, old.summary);
            END;

            CREATE TRIGGER IF NOT EXISTS news_au AFTER UPDATE ON news BEGIN
                INSERT INTO news_fts(news_fts, rowid, title, full_content, summary)
                VALUES ('delete', old.id, old.title, old.full_content, old.summary);
                INSERT INTO news_fts(rowid, title, full_content, summary)
                VALUES (new.id, new.title, new.full_content, new.summary);
            END;
        """)

    conn.commit()
    conn.close()
    _initialized = True


def _row_to_dict(row):
    return {
        'title': row['title'],
        'link': row['link'],
        'published': row['published'],
        'summary': row['summary'],
        'full_content': row['full_content'],
        'source': row['source'],
        'image': row['image_url'],
        'original_link': row['source'],
        'sentiment': row['sentiment'],
    }


def load_news_history():
    """
    Backward-compatible: returns dict like the JSON version.
    Auto-migrates from JSON if DB is empty but JSON exists.
    """
    _init_db()
    conn = _get_connection()

    count = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]

    if count == 0 and os.path.exists(JSON_PATH):
        conn.close()
        # Auto-migrate from JSON
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_news_history(data)
            print(f"Auto-migrated {JSON_PATH} to SQLite.")
            return data
        except Exception as e:
            print(f"Auto-migration failed: {e}")
            return {}

    # Build dict from DB
    result = {}
    company_keys = conn.execute(
        "SELECT DISTINCT company_key FROM news"
    ).fetchall()

    for row in company_keys:
        key = row['company_key']
        items = conn.execute(
            "SELECT * FROM news WHERE company_key = ? ORDER BY published DESC",
            (key,)
        ).fetchall()
        result[key] = [_row_to_dict(item) for item in items]

    # Load metadata
    meta_rows = conn.execute("SELECT key, value FROM metadata").fetchall()
    for row in meta_rows:
        result[row['key']] = row['value']

    conn.close()
    return result


def save_news_history(news_data):
    """
    Backward-compatible: accepts the same dict structure as JSON version.
    Upserts news items (dedup by company_key + title).
    """
    _init_db()
    conn = _get_connection()

    for key, items in news_data.items():
        if key.startswith('_'):
            # Metadata
            value = items if isinstance(items, str) else json.dumps(items)
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )
            continue

        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO news
                    (company_key, title, link, published, summary, full_content, source, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    item.get('title', ''),
                    item.get('link', ''),
                    item.get('published', ''),
                    item.get('summary', ''),
                    item.get('full_content', ''),
                    item.get('original_link', item.get('link', '')),
                    item.get('image', '')
                ))
            except Exception as e:
                print(f"Error inserting news item: {e}")

    conn.commit()
    conn.close()
    print("News history saved to SQLite.")


def search_news(query, company_key=None, limit=50):
    """
    Full-text search using FTS5.
    Returns list of news dicts matching the query.
    """
    _init_db()
    conn = _get_connection()

    if company_key:
        rows = conn.execute("""
            SELECT news.* FROM news
            JOIN news_fts ON news.id = news_fts.rowid
            WHERE news_fts MATCH ? AND news.company_key = ?
            ORDER BY rank
            LIMIT ?
        """, (query, company_key, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT news.* FROM news
            JOIN news_fts ON news.id = news_fts.rowid
            WHERE news_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()

    conn.close()
    return [_row_to_dict(row) for row in rows]


def get_news_by_company(company_key, year=None, month=None, limit=100, offset=0):
    """Efficient paginated query for news by company."""
    _init_db()
    conn = _get_connection()

    query = "SELECT * FROM news WHERE company_key = ?"
    params = [company_key]

    if year:
        query += " AND CAST(strftime('%Y', published) AS INTEGER) = ?"
        params.append(year)
    if month:
        query += " AND CAST(strftime('%m', published) AS INTEGER) = ?"
        params.append(month)

    query += " ORDER BY published DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


def get_news_count(company_key=None):
    """Count news items, optionally filtered by company."""
    _init_db()
    conn = _get_connection()

    if company_key:
        count = conn.execute(
            "SELECT COUNT(*) FROM news WHERE company_key = ?", (company_key,)
        ).fetchone()[0]
    else:
        count = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]

    conn.close()
    return count


def get_metadata(key):
    """Get a metadata value."""
    _init_db()
    conn = _get_connection()
    row = conn.execute(
        "SELECT value FROM metadata WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row['value'] if row else None


def set_metadata(key, value):
    """Set a metadata value."""
    _init_db()
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


def update_sentiment(news_id, sentiment):
    """Update sentiment for a specific news item."""
    _init_db()
    conn = _get_connection()
    conn.execute(
        "UPDATE news SET sentiment = ? WHERE id = ?",
        (sentiment, news_id)
    )
    conn.commit()
    conn.close()
