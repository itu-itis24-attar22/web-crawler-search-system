from flask import Flask, request, redirect, url_for, render_template, jsonify
from services.job_manager import JobManager
from services.crawler_service import CrawlerService
from services.search_service import SearchService
from utils.file_store import tail_lines, crawler_log_path, crawler_queue_path

app = Flask(__name__, template_folder="demo/templates", static_folder="demo/static")

manager = JobManager()
crawler_svc = CrawlerService(manager)
search_svc = SearchService(manager)

@app.route("/")
def index():
    return redirect(url_for("crawler_home"))

@app.route("/crawler", methods=["GET", "POST"])
def crawler_home():
    error = None
    if request.method == "POST":
        origin_url = request.form.get("origin_url", "")
        max_depth = request.form.get("max_depth", "2")
        hit_rate_seconds = request.form.get("hit_rate_seconds", "0")
        max_urls_to_visit = request.form.get("max_urls_to_visit", "10")
        queue_capacity = request.form.get("queue_capacity", "100")
        
        try:
            crawler_id = crawler_svc.create_crawler(
                origin_url, max_depth, hit_rate_seconds, max_urls_to_visit, queue_capacity
            )
            return redirect(url_for("crawler_status_page", crawler_id=crawler_id))
        except ValueError as e:
            error = str(e)
            
    crawlers = crawler_svc.list_crawlers()
    return render_template("crawler.html", crawlers=crawlers, error=error)

@app.route("/crawler/<crawler_id>")
def crawler_status_page(crawler_id):
    job = crawler_svc.get_crawler_status(crawler_id)
    if not job:
        return "Crawler not found", 404
    return render_template("crawler_status.html", job=job)

@app.route("/api/crawler/<crawler_id>/status")
def crawler_status_api(crawler_id):
    job = crawler_svc.get_crawler_status(crawler_id)
    if not job:
        return jsonify({"error": "not found"}), 404
        
    log_tail = tail_lines(crawler_log_path(crawler_id), n=50)
    queue_preview = tail_lines(crawler_queue_path(crawler_id), n=50)
    
    response_data = dict(job)
    response_data["log_tail"] = log_tail
    response_data["queue_preview"] = queue_preview
    return jsonify(response_data)

@app.route("/search")
def search_page():
    query = request.args.get("query", "").strip()
    results = []
    if query:
        results = search_svc.search(query)
    return render_template("search.html", query=query, results=results)

if __name__ == "__main__":
    app.run(port=5000, debug=True, threaded=True)
