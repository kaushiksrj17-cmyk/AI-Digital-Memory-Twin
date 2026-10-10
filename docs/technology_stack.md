# Technology Stack

## ECHO Architecture Specifications

### 1. Frontend Architecture
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.6
- **UI Framework**: React 18.3
- **Styling**: Tailwind CSS 3.4 with Custom Memorial Palette (`slate`, `indigo`, `gold`, `confidence`)
- **Icons**: Lucide React
- **Spatial / Visual Presence**: Three.js / React Three Fiber abstraction for 3D Memory Room sanctuaries
- **Design Paradigm**: Research-grade memorial aesthetic, dark/light theme switching, responsive grid, zero excessive animations

### 2. Backend Architecture
- **Runtime**: Python 3.11+
- **API Framework**: FastAPI 0.111+ with Pydantic v2
- **Configuration**: `pydantic-settings` with `.env` loading and strict validation
- **Concurrency**: Asynchronous event loop (`async`/`await`), WebSocket bidirectional streams
- **Logging**: Structured console logger with audit tracing
- **Security**: JWT (`python-jose`), bcrypt password hashing (`passlib`), regex boundary filters

### 3. Database & Data Abstractions
- **Relational Metadata**: PostgreSQL-ready architecture with SQLAlchemy 2.0 async engine and SQLite local fallback
- **Vector Database**: Pluggable abstraction supporting Qdrant and local in-memory cosine vector store
- **Knowledge Graph**: Entity-relationship abstraction supporting Neo4j and in-memory adjacency graph
- **Repository Pattern**: Clean decoupling between service layer and database persistence

### 4. Multimodal AI Providers
- **LLM**: Pluggable `BaseLLMProvider` (Google Gemini 1.5 Pro adapter and offline `MockLLMProvider`)
- **Embeddings**: `BaseEmbeddingProvider` (`text-embedding-004` adapter and deterministic offline mock)
- **Speech-to-Text (STT)**: `BaseSTTProvider` (Whisper API / local mock)
- **Text-to-Speech (TTS)**: `BaseTTSProvider` (Watermarked synthetic voice / local mock)
- **Computer Vision**: `BaseVisionProvider` (Scene description, object detection, face clustering)
- **OCR**: `BaseOCRProvider` (Document text digitization, handwriting extraction)

### 5. Private Storage & Boundary Controls
- **Storage Subsystem**: Strictly isolated within `D:\ECHO\storage\local`
- **Upload Directory**: `D:\ECHO\storage\local\uploads`
- **Cache Directory**: `D:\ECHO\storage\local\cache`
- **Encrypted Directory**: `D:\ECHO\storage\local\encrypted`
- **Encryption**: AES-256-GCM architecture ready for Phase 2 zero-knowledge client encryption

### 6. Containerization & Deployment
- **Docker**: Multi-stage `Dockerfile.backend` and `Dockerfile.frontend`
- **Orchestration**: `docker-compose.yml` supporting backend, frontend, PostgreSQL (pgvector), and Qdrant
