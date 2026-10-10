# API Overview & Endpoints

## REST API Specification (`/api/v1`)

The ECHO API provides modular, versioned REST endpoints and real-time WebSockets. All requests and responses are strictly typed via Pydantic v2 schemas.

---

### Core Endpoint Summary

| Module | Endpoint | Method | Description |
|---|---|---|---|
| **Health** | `/api/v1/health` | `GET` | System diagnostic, D:\ECHO storage verification, provider readiness |
| **Auth** | `/api/v1/auth/login` | `POST` | Authenticate memorial guardian credentials |
| **Auth** | `/api/v1/auth/me` | `GET` | Retrieve current authenticated user profile |
| **Users** | `/api/v1/users/` | `GET` | List authorized family trustees and kinship circle |
| **Memories** | `/api/v1/memories/` | `GET` | List memories with search, category, media type, and privacy filters |
| **Memories** | `/api/v1/memories/{id}` | `GET` | Retrieve individual memory with full provenance citations |
| **Memories** | `/api/v1/memories/` | `POST` | Ingest new memory into vault with SHA-256 duplicate detection |
| **Memories** | `/api/v1/memories/{id}` | `PUT` | Update memory metadata, spatiotemporal anchors, or privacy |
| **Memories** | `/api/v1/memories/{id}` | `DELETE` | Soft-delete memory from active vault with audit logging |
| **Memories** | `/api/v1/memories/{id}/archive` | `POST` | Archive memory (preserves file and history, hides from active view) |
| **Memories** | `/api/v1/memories/{id}/verify` | `POST` | Update verification status (VERIFIED, PENDING_REVIEW, REJECTED) |
| **Memories** | `/api/v1/memories/{id}/export` | `POST` | Generate JSON archival export bundle with safe relative media link |
| **Media** | `/api/v1/media/` | `GET` | List preserved media assets in vault |
| **Media** | `/api/v1/media/{id}` | `GET` | Retrieve media metadata or stream secure file (`?download=true`) |
| **Media** | `/api/v1/media/upload` | `POST` | Securely upload media into `storage/originals` (Validates MIME, SHA-256) |
| **Media** | `/api/v1/media/{id}` | `DELETE` | Safely remove media asset from vault storage |
| **Consent** | `/api/v1/consent/` | `POST` | Grant explicit guardian consent (Media, AI, Voice, Avatar, Family) |
| **Consent** | `/api/v1/consent/` | `GET` | Query active or historical consent records |
| **Consent** | `/api/v1/consent/{id}/revoke`| `POST` | Revoke previously granted consent authorization |
| **Audit** | `/api/v1/audit/` | `GET` | Query tamper-evident audit history of vault operations |
| **Timeline** | `/api/v1/timeline/` | `GET` | Retrieve chronological life events with spatiotemporal anchors |
| **People** | `/api/v1/people/` | `GET` | List individuals associated with the memorialized subject |
| **Relationships** | `/api/v1/relationships/`| `GET` | Retrieve kinship edges and closeness ratings |
| **Conversation** | `/api/v1/conversation/sessions` | `GET` | List dialogue sessions |
| **Conversation** | `/api/v1/conversation/sessions/{id}` | `GET` | Retrieve session transcript |
| **Conversation** | `/api/v1/conversation/sessions/{id}/messages` | `POST` | Post inquiry, receive evidence-grounded response with disclaimer |
| **RAG** | `/api/v1/rag/query` | `POST` | Retrieve evidence chunks and citations for grounding |
| **Embeddings** | `/api/v1/embeddings/generate` | `POST` | Generate semantic vector embeddings |
| **Voice** | `/api/v1/voice/status` | `GET` | Check STT / TTS engine readiness and watermarking policies |
| **Voice** | `/api/v1/voice/synthesize` | `POST` | Synthesize memorial speech snippet with AI disclosure |
| **Avatar** | `/api/v1/avatar/status` | `GET` | Inspect visual presence engine and Three.js shader pipeline |
| **Provenance** | `/api/v1/provenance/citations` | `GET` | List authenticated provenance citations |
| **Confidence** | `/api/v1/confidence/levels` | `GET` | Retrieve system confidence levels (GREEN, YELLOW, RED) |
| **Guardian** | `/api/v1/guardian/status` | `GET` | Inspect Memory Guardian active monitoring rules |
| **Guardian** | `/api/v1/guardian/audit` | `POST` | Audit text for consciousness claims and ethical violations |
| **Security** | `/api/v1/security/status` | `GET` | Inspect vault isolation posture and encryption parameters |
| **Analytics** | `/api/v1/analytics/dashboard` | `GET` | Retrieve live aggregate metrics for executive memorial dashboard |
| **Processing** | `/api/v1/processing/{media_id}` | `POST` | Enqueue media for multimodal evidence processing |
| **Processing** | `/api/v1/processing/{media_id}` | `GET` | Get status, latency, and error message for a processing job |
| **Processing** | `/api/v1/processing` | `GET` | List all active and historical processing jobs in the queue |
| **Processing** | `/api/v1/processing/{media_id}/retry` | `POST` | Retry a failed or review-required processing job |
| **Processing** | `/api/v1/processing/{media_id}/cancel` | `POST` | Cancel a pending processing job |
| **Evidence** | `/api/v1/evidence` | `GET` | Query atomic evidence records with filtering (type, provenance, confidence) |
| **Evidence** | `/api/v1/evidence/{id}` | `GET` | Retrieve specific evidence item with citation and structured value |
| **Media Derivation** | `/api/v1/media/{id}/metadata` | `GET` | Retrieve normalized cross-modal technical metadata |
| **Media Derivation** | `/api/v1/media/{id}/ocr` | `GET` | Retrieve OCR extracted text and bounding-box data |
| **Media Derivation** | `/api/v1/media/{id}/transcript` | `GET` | Retrieve STT audio transcript with timestamped segments |
| **Media Derivation** | `/api/v1/media/{id}/keyframes` | `GET` | Retrieve extracted video keyframe records and paths |
| **Entities** | `/api/v1/memories/{id}/entities` | `GET` | List extracted entities (Person, Location, Organization, Date) for memory |
| **Events** | `/api/v1/memories/{id}/events` | `GET` | List documented life milestone events for memory |
| **Analytics** | `/api/v1/analytics/processing` | `GET` | Retrieve research telemetry on processing queue and confidence metrics |
| **Memory DNA** | `/api/v1/memory-dna/build/{id}` | `POST` | Compile 22-category evidence-grounded Memory DNA document |
| **Memory DNA** | `/api/v1/memory-dna/{id}` | `GET` | Retrieve active Memory DNA profile |
| **Memory DNA** | `/api/v1/memory-dna/{id}/history` | `GET` | Retrieve historical snapshots of Memory DNA for reproducibility |
| **Memory DNA** | `/api/v1/memory-dna/{id}/items` | `GET` | Query granular Memory DNA items with category & confidence filters |
| **Memory DNA** | `/api/v1/memory-dna/items/{id}/verify` | `POST` | Manually verify Memory DNA item with primary evidence backing |
| **Memory DNA** | `/api/v1/memory-dna/items/{id}/reject` | `POST` | Reject unsupported Memory DNA item |
| **Knowledge Graph** | `/api/v1/graph/nodes` | `GET` | Query nodes (Person, Memory, Event, Place, Org, Date, etc.) |
| **Knowledge Graph** | `/api/v1/graph/nodes/{id}/neighbors` | `GET` | Traverse 1-to-N neighborhood edges and connected entities |
| **Knowledge Graph** | `/api/v1/graph/relationships` | `GET` | List all evidence-backed relationship edges |
| **Knowledge Graph** | `/api/v1/graph/search` | `GET` | Search graph entities and related subgraph connections |
| **Knowledge Graph** | `/api/v1/graph/rebuild/{id}` | `POST` | Safely compile knowledge graph from memories and entities |
| **Knowledge Graph** | `/api/v1/graph/stats` | `GET` | Retrieve node and relationship breakdown metrics |
| **Vector Index** | `/api/v1/embeddings/index/{id}` | `POST` | Chunk and embed archival records into vector store |
| **Vector Index** | `/api/v1/embeddings/stats` | `GET` | Inspect indexed vector counts and vector store readiness |
| **Vector Index** | `/api/v1/embeddings/{id}` | `DELETE` | Delete specific vector entry from vector index |
| **Retrieval** | `/api/v1/retrieval/search` | `POST` | Multi-strategy evidence retrieval (VECTOR, KEYWORD, GRAPH, HYBRID) |
| **Retrieval** | `/api/v1/retrieval/history` | `GET` | Inspect historical retrieval queries, latency, and candidate counts |
| **RAG Query** | `/api/v1/rag/query` | `POST` | Execute evidence-grounded RAG query with 18-check Guardian audit |
| **RAG Telemetry** | `/api/v1/rag/metrics` | `GET` | Retrieve RAG latency, evidence coverage, and claim counts |
| **Memory Guardian** | `/api/v1/guardian/validate` | `POST` | Audit candidate response text, claims, and evidence |
| **Memory Guardian** | `/api/v1/guardian/status` | `GET` | Inspect real-time Guardian enforcement state |
| **Memory Guardian** | `/api/v1/guardian/audit` | `GET` | Retrieve historical Guardian validation logs and verdicts |
| **Conversations** | `/api/v1/conversations` | `POST` | Create a new conversational memorial dialogue session |
| **Conversations** | `/api/v1/conversations/sessions` | `GET` | List active memorial dialogue sessions |
| **Conversations** | `/api/v1/conversations/{id}` | `GET` | Retrieve session transcript, sources, and guardian verdicts |
| **Conversations** | `/api/v1/conversations/{id}/messages` | `POST` | Post user query, run RAG, and receive validated assistant message |
| **Conversations** | `/api/v1/conversations/{id}/export` | `POST` | Export tamper-evident session transcript with evidence citations |
| **Conversations** | `/api/v1/conversations/{id}` | `DELETE` | Delete conversational dialogue session |

---

### Real-Time WebSocket Interface
- **Endpoint**: `ws://127.0.0.1:8000/ws/conversation/{session_id}`
- **Protocol**: JSON-based message streaming with automatic ethical disclaimer handshake and live lifecycle events (`RETRIEVING`, `CONTEXT_READY`, `GENERATING`, `VALIDATING`, `COMPLETED`, `BLOCKED`, `ERROR`).

