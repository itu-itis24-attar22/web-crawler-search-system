import time
import datetime
import threading
import uuid
from collections import deque

from services.job_manager import JobManager
from utils.file_store import *
from utils.url_utils import normalize_url, should_skip_url
from utils.html_fetcher import fetch_html
from utils.html_parser import extract_text_and_links
from utils.tokenizer import count_words

class CrawlerService:
    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager

    def create_crawler(self, origin_url, max_depth, hit_rate_seconds, max_urls_to_visit, queue_capacity) -> str:
        origin_url = origin_url.strip()
        if not origin_url or not origin_url.startswith(("http://", "https://")):
            raise ValueError("Invalid origin URL.")
        norm_url = normalize_url(origin_url)
        if not norm_url:
            raise ValueError("Invalid normalized origin URL.")
        
        try:
            max_depth = int(max_depth)
            if not (0 <= max_depth <= 5):
                raise ValueError("max_depth must be between 0 and 5.")
                
            hit_rate_seconds = float(hit_rate_seconds)
            if not (0 <= hit_rate_seconds <= 10):
                raise ValueError("hit_rate_seconds must be between 0 and 10.")
                
            max_urls_to_visit = int(max_urls_to_visit)
            if not (1 <= max_urls_to_visit <= 500):
                raise ValueError("max_urls_to_visit must be between 1 and 500.")
                
            queue_capacity = int(queue_capacity)
            if not (1 <= queue_capacity <= 2000):
                raise ValueError("queue_capacity must be between 1 and 2000.")
        except ValueError as e:
            raise ValueError(f"Validation failed: {e}")

        Epoch_time = int(time.time())
        crawler_id = f"{Epoch_time}_{uuid.uuid4().hex[:8]}"

        now = datetime.datetime.now(datetime.UTC).isoformat()
        job_data = {
            "crawler_id": crawler_id,
            "origin_url": norm_url,
            "max_depth": max_depth,
            "hit_rate_seconds": hit_rate_seconds,
            "max_urls_to_visit": max_urls_to_visit,
            "queue_capacity": queue_capacity,
            "status": "running",
            "created_at": now,
            "updated_at": now,
            "processed_count": 0,
            "discovered_count": 0,
            "queued_count": 1,
            "throttled": False,
            "throttled_ever": False,
            "error_message": ""
        }

        write_json(crawler_data_path(crawler_id), job_data)
        rewrite_queue_file(crawler_id, [(0, norm_url)])
        append_log(crawler_id, f"START origin={norm_url} depth={max_depth}")
        
        thread = threading.Thread(target=self._run_crawler, args=(crawler_id,), daemon=True)
        self.job_manager.register_job(job_data, thread)
        thread.start()
        
        return crawler_id

    def get_crawler_status(self, crawler_id: str) -> dict | None:
        return self.job_manager.get_job(crawler_id)

    def list_crawlers(self) -> list[dict]:
        return self.job_manager.list_jobs()

    def _persist_job_state(self, crawler_id: str, job_data: dict) -> None:
        job_data["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        write_json(crawler_data_path(crawler_id), job_data)
        self.job_manager.update_job(crawler_id, job_data)
    def _sync_queue_state(self, crawler_id: str, job: dict, queue: deque) -> None:
        rewrite_queue_file(crawler_id, list(queue))
        job["queued_count"] = len(queue)
        job["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        write_json(crawler_data_path(crawler_id), job)
        self.job_manager.update_job(crawler_id, job)

    def _load_runtime_queue(self, crawler_id: str, origin_url: str) -> deque:
        q = deque()
        lines = read_lines(crawler_queue_path(crawler_id))
        if lines:
            for line in lines:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    q.append((int(parts[0]), parts[1]))
        else:
            q.append((0, origin_url))
        return q

    def _run_crawler(self, crawler_id: str) -> None:
        job = self.job_manager.get_job(crawler_id)
        if not job:
            return
            
        try:
            queue = self._load_runtime_queue(crawler_id, job["origin_url"])
            
            while queue and job["processed_count"] < job["max_urls_to_visit"] and job["status"] == "running":
                depth, url = queue.popleft()
                self._sync_queue_state(crawler_id, job, queue)
                
                if depth > job["max_depth"]:
                    append_log(crawler_id, f"SKIP depth limit url={url}")
                    continue
                    
                norm_url = normalize_url(url)
                if not norm_url:
                    append_log(crawler_id, f"SKIP invalid normalized url={url}")
                    continue
                    
                if not self.job_manager.mark_visited(norm_url):
                    append_log(crawler_id, f"SKIP already visited url={norm_url}")
                    continue
                    
                if job["hit_rate_seconds"] > 0:
                    time.sleep(job["hit_rate_seconds"])
                    
                append_log(crawler_id, f"FETCH_START depth={depth} url={norm_url}")
                
                status_code, ctype, html_text = fetch_html(norm_url, timeout=10)
                
                if status_code == 0:
                    append_log(crawler_id, f"FETCH_FAIL url={norm_url}")
                    continue
                if not (200 <= status_code < 300):
                    append_log(crawler_id, f"FETCH_NON_200 status={status_code} url={norm_url}")
                    continue
                if "text/html" not in ctype.lower():
                    append_log(crawler_id, f"FETCH_SKIP_NON_HTML type={ctype} url={norm_url}")
                    continue
                if not html_text.strip():
                    append_log(crawler_id, f"FETCH_EMPTY url={norm_url}")
                    continue
                    
                visible_text, links = extract_text_and_links(html_text, norm_url)
                
                words_freq = count_words(visible_text)
                
                with self.job_manager.word_file_lock:
                    for word, freq in words_freq.items():
                        append_word_record(word, norm_url, job["origin_url"], depth, freq)
                        
                append_log(crawler_id, f"INDEX words_unique={len(words_freq)} links_found={len(links)} url={norm_url}")
                
                added_this_page = 0
                for child_link in links:
                    if depth + 1 > job["max_depth"]:
                        continue

                    child_norm = normalize_url(child_link)
                    if not child_norm or should_skip_url(child_norm):
                        continue

                    if child_norm == norm_url:
                        continue

                    if any(existing_url == child_norm for _, existing_url in queue):
                        continue

                    if len(queue) < job["queue_capacity"]:
                        queue.append((depth + 1, child_norm))
                        added_this_page += 1
                    else:
                        job["throttled"] = True
                        job["throttled_ever"] = True
                        append_log(crawler_id, f"THROTTLED queue_capacity={job['queue_capacity']} url={child_norm}")
                        break
                            
                if len(queue) < job["queue_capacity"]:
                    job["throttled"] = False
                    
                job["processed_count"] += 1
                job["discovered_count"] += len(links)
                job["queued_count"] = len(queue)
                
                self._persist_job_state(crawler_id, job)
                rewrite_queue_file(crawler_id, list(queue))

            if job["status"] == "running":
                job["queued_count"] = len(queue)
                rewrite_queue_file(crawler_id, list(queue))
                job["status"] = "completed"
                append_log(crawler_id, f"COMPLETE processed={job['processed_count']}")
                self._persist_job_state(crawler_id, job)
                
        except Exception as e:
            job["status"] = "failed"
            job["error_message"] = str(e)
            append_log(crawler_id, f"FAILED error={str(e)}")
            self._persist_job_state(crawler_id, job)
