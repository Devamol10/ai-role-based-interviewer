# Relational and NoSQL Databases

## Indexing and Query Performance
Database indexing utilizes B-Trees and Hash Indexes to accelerate lookup queries from O(N) to O(log N). Composite indexes require strict compliance with the Leftmost Prefix Rule. Unindexed JOIN operations or wildcard leading LIKE queries (`%term`) force full table scans, resulting in severe I/O degradation.

## Transactional Isolation Levels & ACID
ACID guarantees ensure database integrity under concurrent workloads:
- **Atomicity**: All operations commit or roll back completely.
- **Consistency**: Invariants and constraints remain valid before and after transactions.
- **Isolation**: Prevents concurrency anomalies. ANSI SQL levels include Read Uncommitted, Read Committed, Repeatable Read, and Serializable. Higher isolation levels mitigate Dirty Reads, Non-Repeatable Reads, and Phantom Reads using Two-Phase Locking (2PL) or Multi-Version Concurrency Control (MVCC).
- **Durability**: Committed write transactions are flushed to Write-Ahead Logs (WAL) before confirmation.

## Database Sharding vs. Replication
Primary-replica replication delegates write traffic to the primary node while scaling read queries across replicas. Database sharding partitions datasets horizontally across multiple distinct nodes using hash-based or range-based partition keys.
