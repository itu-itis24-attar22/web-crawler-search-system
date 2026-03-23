import os
from services.job_manager import JobManager
from utils.tokenizer import tokenize_text
from utils.file_store import word_file_path
from utils.ranking import collapse_query_matches, sort_search_results

class SearchService:
    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager

    def search(self, query: str) -> list[dict]:
        tokens = tokenize_text(query)
        unique_tokens = list(set(tokens))
        
        if not unique_tokens:
            return []
            
        raw_matches = []
        for token in unique_tokens:
            filepath = word_file_path(token)
            
            with self.job_manager.word_file_lock:
                if not os.path.exists(filepath):
                    continue
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) == 5:
                    if parts[0] == token:
                        raw_matches.append({
                            "word": parts[0],
                            "relevant_url": parts[1],
                            "origin_url": parts[2],
                            "depth": int(parts[3]),
                            "frequency": int(parts[4])
                        })
                        
        aggregated = collapse_query_matches(raw_matches)
        sorted_results = sort_search_results(aggregated)
        
        return sorted_results
