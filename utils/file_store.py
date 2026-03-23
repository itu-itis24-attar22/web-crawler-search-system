import os
import json
import datetime
import glob

STORAGE_DIR = "storage"
CRAWLERS_DIR = os.path.join(STORAGE_DIR, "crawlers")
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
QUEUES_DIR = os.path.join(STORAGE_DIR, "queues")
WORDS_DIR = os.path.join(STORAGE_DIR, "words")
VISITED_FILE = os.path.join(STORAGE_DIR, "visited_urls.data")

def ensure_storage_layout():
    for d in [STORAGE_DIR, CRAWLERS_DIR, LOGS_DIR, QUEUES_DIR, WORDS_DIR]:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(VISITED_FILE):
        open(VISITED_FILE, 'a', encoding='utf-8').close()

def read_json(path) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def write_json(path, data) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def append_line(path, line) -> None:
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f"{line}\n")

def read_lines(path) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def tail_lines(path, n=100) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        return lines[-n:]

def crawler_data_path(crawler_id) -> str:
    return os.path.join(CRAWLERS_DIR, f"{crawler_id}.data.json")

def crawler_log_path(crawler_id) -> str:
    return os.path.join(LOGS_DIR, f"{crawler_id}.log")

def crawler_queue_path(crawler_id) -> str:
    return os.path.join(QUEUES_DIR, f"{crawler_id}.queue")

def word_file_path(word) -> str:
    if not word:
        return os.path.join(WORDS_DIR, "misc.data")
    first_char = word[0].lower()
    if 'a' <= first_char <= 'z':
        return os.path.join(WORDS_DIR, f"{first_char}.data")
    return os.path.join(WORDS_DIR, "misc.data")

def load_visited_urls() -> set:
    lines = read_lines(VISITED_FILE)
    return set(lines)

def append_visited_url(url) -> None:
    append_line(VISITED_FILE, url)

def append_queue_item(crawler_id, depth, url) -> None:
    path = crawler_queue_path(crawler_id)
    append_line(path, f"{depth}\t{url}")

def rewrite_queue_file(crawler_id, queue_items) -> None:
    path = crawler_queue_path(crawler_id)
    with open(path, 'w', encoding='utf-8') as f:
        for depth, url in queue_items:
            f.write(f"{depth}\t{url}\n")

def append_log(crawler_id, message) -> None:
    path = crawler_log_path(crawler_id)
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    # format: 2026-03-19T14:05:10 START origin=https://...
    append_line(path, f"{timestamp} {message}")

def append_word_record(word, relevant_url, origin_url, depth, frequency) -> None:
    path = word_file_path(word)
    record = f"{word}\t{relevant_url}\t{origin_url}\t{depth}\t{frequency}"
    append_line(path, record)

def load_crawler_records() -> list[dict]:
    records = []
    pattern = os.path.join(CRAWLERS_DIR, "*.data.json")
    for filepath in glob.glob(pattern):
        data = read_json(filepath)
        if data:
            records.append(data)
    
    records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return records
