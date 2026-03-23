# Recommendation

## Next Steps for Production

Filesystem storage should be replaced with a more durable and query-efficient storage layer. Visited URLs, crawler metadata, and index data should move to a database or key-value store. Crawler workers and search-serving components should be separated more cleanly, and search index updates should be exposed through a safer incremental indexing model.

Production deployment would need stronger throttling and crawl politeness, as well as better monitoring and alerting for crawler health, queue behavior, and search latency. The system needs improved recovery semantics, safer concurrency control, and a stronger security/compliance posture. Finally, relevance should later expand beyond simple keyword frequency and depth.
