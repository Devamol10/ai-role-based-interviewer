# Caching Strategies & Distributed In-Memory Caching

## Caching Patterns
1. **Cache-Aside (Lazy Loading)**: The application checks the cache first. If a cache miss occurs, data is fetched from the primary database and stored in the cache.
2. **Write-Through**: Data is simultaneously written to the cache and primary storage, reducing read latency at the cost of write latency.
3. **Write-Behind (Write-Back)**: Writes are buffered in memory and asynchronously flushed to the database, optimizing throughput but risking data loss upon sudden node crashes.

## Cache Invalidation and Eviction Policies
Cache invalidation remains a core challenge in distributed engineering. Common eviction algorithms include:
- **LRU (Least Recently Used)**: Evicts keys that haven't been accessed for the longest duration.
- **LFU (Least Frequently Used)**: Evicts items with the lowest access frequency count.
- **TTL (Time-To-Live)**: Automatically expires records after a defined duration to mitigate stale state.

## Cache Stampede Mitigation
A Cache Stampede (Thundering Herd Problem) occurs when a high-traffic key expires, triggering concurrent database reads. Mitigations include Mutex Locking (Singleflight), Probabilistic Early Expiration (XFetch algorithm), and background refreshing.
