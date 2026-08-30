# RESTful and Modern API Architecture

## HTTP Semantics and Idempotency
RESTful APIs leverage standard HTTP methods to express intent. Idempotency guarantees that multiple identical requests produce the same server state as a single request:
- `GET`, `HEAD`, `OPTIONS`: Safe and idempotent.
- `PUT`, `DELETE`: Idempotent (subsequent calls maintain identical state).
- `POST`: Non-idempotent (creates new resource instances).
- `PATCH`: Non-idempotent unless explicitly designed with atomic patch operations.

## Rate Limiting and Traffic Management
Rate limiting protects upstream application services from noisy neighbors and denial-of-service attempts. Common algorithms include:
1. **Token Bucket**: Allows burst capacity while maintaining steady refill rate.
2. **Leaky Bucket**: Enforces smooth output processing rates.
3. **Sliding Window Log**: Offers precise rate enforcement by logging timestamped request tokens.

## Microservices Communication: gRPC vs REST
While REST over JSON provides high interoperability and human-readable payload formats, gRPC utilizes Protocol Buffers over HTTP/2 to provide strictly typed contracts, compact binary serialization, and bidirectional streaming.
