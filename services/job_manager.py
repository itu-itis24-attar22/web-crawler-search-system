import threading
from utils.file_store import *
from utils.url_utils import normalize_url

class JobManager:
    def __init__(self):
        self.visited_lock = threading.Lock()
        self.job_state_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        self.word_file_lock = threading.Lock()
        
        ensure_storage_layout()
        
        self.visited_set = load_visited_urls()
        
        self.jobs_by_id = {}
        self.threads_by_id = {}
        
        records = load_crawler_records()
        for record in records:
            job_id = record.get("crawler_id")
            if not job_id:
                continue
            
            status = record.get("status", "")
            if status in ("running", "queued"):
                record["status"] = "interrupted"
                write_json(crawler_data_path(job_id), record)
            
            self.jobs_by_id[job_id] = record

    def register_job(self, job_data: dict, thread: threading.Thread = None):
        with self.job_state_lock:
            job_id = job_data["crawler_id"]
            self.jobs_by_id[job_id] = job_data
            if thread:
                self.threads_by_id[job_id] = thread

    def update_job(self, crawler_id: str, updates: dict):
        with self.job_state_lock:
            if crawler_id in self.jobs_by_id:
                self.jobs_by_id[crawler_id].update(updates)

    def get_job(self, crawler_id: str) -> dict | None:
        with self.job_state_lock:
            return self.jobs_by_id.get(crawler_id)

    def list_jobs(self) -> list[dict]:
        with self.job_state_lock:
            jobs = list(self.jobs_by_id.values())
            jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return jobs

    def mark_visited(self, url: str) -> bool:
        with self.visited_lock:
            url = normalize_url(url)
            if url in self.visited_set:
                return False
            self.visited_set.add(url)
            append_visited_url(url)
            return True
