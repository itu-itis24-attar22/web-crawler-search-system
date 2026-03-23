# Product PRD

## 1. Objective
The goal is to build a local web crawler and search system. It must expose two capabilities: index and search. The index must crawl from an origin URL up to depth k. The search must return relevant URLs as triples: (relevant_url, origin_url, depth), and search must work while indexing is still active.

## 2. Scope
- local execution on localhost
- recursive crawling to max depth
- visited set to avoid duplicate crawling
- queue-based crawling
- filesystem-based persistence
- simple relevance ranking using frequency and depth
- web UI for starting crawls, viewing status, and searching
- real-time polling for crawler status
This prototype is intentionally single-machine and simple.

## 3. Core User Flows
**Flow A — Start crawl:**
User enters origin URL, max depth, hit rate, max URLs, and queue capacity. System creates crawler job, starts background thread, and shows status page.

**Flow B — Monitor crawl:**
User opens crawler status page and sees status, processed count, queue depth, throttled status, logs, and queue preview.

**Flow C — Search:**
User enters query and receives relevant URL, origin URL, depth. Search can return partial results while indexing is still ongoing.

## 4. Functional Requirements
1. The system shall expose an indexing capability that accepts origin and k.
2. The indexer shall crawl pages recursively up to depth k.
3. The indexer shall not crawl the same page twice.
4. The system shall manage crawl load using back pressure.
5. The system shall expose a search capability that accepts a query string.
6. The searcher shall return triples of (relevant_url, origin_url, depth).
7. The searcher shall work while indexing is active.
8. The system shall provide a UI for starting crawls and searches.
9. The system shall display crawler state including queue depth and throttling status.
10. The system shall persist crawl artifacts to local storage.
11. The system may support partial recovery after interruption.

## 5. Non-Functional Requirements
- must run on a single local machine
- must use native language functionality for the core crawler behavior
- must be thread-safe for shared indexing/search state
- must remain understandable and maintainable
- must prefer correctness and clarity over feature breadth
- must be runnable by a reviewer without external infrastructure

## 6. System Components
**Crawler Service:** Starts and manages crawler jobs.
**Search Service:** Executes query lookup over indexed data.
**Storage Layer:** Stores crawler metadata, queue state, logs, visited URLs, and word index files.
**Web UI:** Provides pages for crawl creation, crawl status, and search.

## 7. Data and Storage Model
Files utilized:
`storage/visited_urls.data`
`storage/crawlers/{crawler_id}.data.json`
`storage/logs/{crawler_id}.log`
`storage/queues/{crawler_id}.queue`
`storage/words/a.data` through `z.data` and `misc.data`

The visited file prevents duplicate crawling. The crawler data file stores job metadata and counters. The queue file supports visibility and partial recovery. The log file supports observability. The word files support search by alphabetical partitioning.

## 8. Relevance Definition
Relevance is defined by keyword frequency in indexed page content, and shallower crawl depth as a secondary preference. Sorting is total frequency descending, depth ascending, URL ascending as a tie-breaker.

## 9. Back Pressure Behavior
Back pressure is implemented using a configurable hit rate delay between requests and a configurable queue capacity per crawler job. When the queue reaches capacity, additional discovered links are not enqueued, the crawler status marks itself as throttled, and throttling state is visible in the UI.

## 10. UI Requirements
The UI provides 3 pages:
- crawler creation page (shows form and recent jobs)
- crawler status page (shows dynamic counts, log tail, queue preview)
- search page (shows exact match results as triples)

## 11. Assumptions
- HTML pages are fetched via simple HTTP GET
- only text/html pages are indexed
- exact keyword matching is sufficient for prototype search
- filesystem storage is acceptable for prototype scope
- crawler runs on one machine only
- query-time partial results are acceptable while indexing is active

## 12. Out of Scope
- distributed crawling
- advanced ranking such as PageRank
- fuzzy search
- NLP / semantic search
- robots.txt compliance enforcement
- authentication
- full browser rendering for JavaScript-heavy sites
- database-backed persistence

## 13. Success Criteria
- can start a crawl from origin and depth
- no duplicate page crawls occur
- search returns expected triples
- search works during active indexing
- queue depth and throttling are visible
- project runs locally
- deliverables are complete
