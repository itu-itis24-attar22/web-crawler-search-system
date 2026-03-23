Web Crawler Demo
Overview

This project is a local prototype web crawler and live search engine built for the assignment. It starts from an origin URL, crawls to depth k, prevents duplicate crawling, indexes words into filesystem buckets, and supports searching while crawlers are active.

Features

Background crawler jobs

Visited URL deduplication

Configurable crawl depth

Configurable hit rate

Queue-capacity-based back pressure

Live crawler status page

Filesystem-backed word index

Live search over indexed content

Local execution on localhost

Architecture
Crawler Service

Handles crawl creation and page indexing.

Search Service

Handles query execution against word index files.

Storage Layer

Handles metadata, queue state, logs, visited URLs, and word buckets.

Web UI

Handles crawl creation, status viewing, and search.

Storage Layout
storage/
├── crawlers/
├── logs/
├── queues/
├── words/
└── visited_urls.data

The visited file prevents duplicate crawling.

Crawler data files store job metadata and counters.

Queue files support visibility and partial recovery.

Log files support observability.

Word files support search by alphabetical partitioning.

How to Run
python -m venv .venv
# activate venv
# On Windows: .venv\Scripts\activate
# On Unix: source .venv/bin/activate
pip install -r requirements.txt
python app.py

Then open your browser at the local address printed by Flask, usually http://127.0.0.1:5000.

How to Use
Start a crawler

Open /crawler, fill in the origin URL, depth, hit rate, max URLs, and queue capacity, then submit the form.

Monitor a crawler

Open a crawler status page and watch logs, queue preview, counts, and throttling state update live.

Search

Open /search, enter a query, and review results as (relevant_url, origin_url, depth). The UI also shows frequency as an additional ranking detail. Partial results may appear while crawlers are still running.

Search Semantics

Search is exact keyword match over indexed tokens. Each matching record links the query word to the relevant URL, origin URL, depth, and frequency. Results are aggregated and sorted by total frequency descending, then by depth ascending.

Back Pressure

Each crawler supports a hit rate delay between requests and a configurable queue capacity. Once capacity is reached, additional discovered links are not enqueued. The crawler status exposes both the current throttling state and whether throttling occurred during the run.

Example Workflow

Start a crawl from https://example.com/ with depth 1 and max 10 URLs.

Open the status page and observe processed pages, queue changes, and logs.

Open /search and query a known indexed word.

Repeat the query while the crawler is still running to observe new results appearing.

Limitations

Filesystem storage instead of a database

No intra-crawler parallel page processing

Exact-match search only

No robots.txt enforcement

No JavaScript rendering

No advanced ranking

Future Improvements

Move index and storage to a database or key-value store

Use a stronger indexing structure

Add stronger crawl politeness and retry logic

Improve search ranking

Improve resume and recovery semantics