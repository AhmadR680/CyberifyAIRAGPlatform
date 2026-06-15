# Cyberify AI Platform

A robust, full-stack Artificial Intelligence platform for Retrieval-Augmented Generation (RAG) and intelligent document processing. The application features multi-LLM routing (OpenAI, Gemini, Groq), a dynamic vector embedding pipeline using PostgreSQL (`pgvector`), real-time Server-Sent Event (SSE) notifications, and a highly polished glassmorphism Next.js UI.

## Setup & Run Instructions

This project is fully containerized using Docker and Docker Compose. You do not need to install local dependencies.

### Prerequisites
- Docker & Docker Compose installed.
- Valid API keys for Google Gemini, OpenAI, or Groq.

### Running Locally

1. **Environment Variables**:
   In the `backend` folder, create a `.env` file containing your credentials:
   ```env
   # backend/.env
   DB_NAME=cyberify
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=postgres
   DB_PORT=5432
   CELERY_BROKER_URL=redis://redis:6379/0

   # AI Provider Keys
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=AIza...
   GROQ_API_KEY=gsk_...
   ```

2. **Start the Infrastructure**:
   In the root directory, run:
   ```bash
   docker compose up --build -d
   ```
   This will spin up:
   - **Postgres Database** (with pgvector)
   - **Redis Cache/Broker**
   - **Django Backend** (on `http://localhost:8000`)
   - **Celery Worker** (for background processing)
   - **Next.js Frontend** (on `http://localhost:3000`)

3. **Database Migrations**:
   Once the containers are running, execute the migrations inside the backend container:
   ```bash
   docker compose exec backend python manage.py makemigrations
   docker compose exec backend python manage.py migrate
   ```

4. **Access the Application**:
   Open `http://localhost:3000` in your web browser. 

---

## API Documentation (Swagger)

The project includes automatically generated OpenAPI (Swagger) documentation via `drf-spectacular`.

With the backend running, visit:
- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## Architecture Diagram

The system uses a decoupled microservices-like architecture:

```mermaid
graph TD
    %% Define styles
    classDef client fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef server fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef worker fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff
    classDef db fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff
    classDef external fill:#64748b,stroke:#334155,stroke-width:2px,color:#fff

    User((User Web Browser)):::client -->|HTTP/REST| NextJS[Next.js Frontend\nReact/Tailwind]:::client
    User -->|Server-Sent Events| RedisPubSub[(Redis Pub/Sub)]:::db

    NextJS <-->|REST API| Django[Django API Backend\nDRF]:::server
    
    Django -->|Schedule Task| CeleryQueue[(Redis Celery Broker)]:::db
    Django <-->|Read/Write Data| Postgres[(PostgreSQL + pgvector)]:::db
    
    CeleryWorker[Celery Background Workers]:::worker <-->|Pop Tasks| CeleryQueue
    CeleryWorker <-->|Write Embeddings| Postgres
    CeleryWorker -->|Push Completion Event| RedisPubSub
    
    CeleryWorker <-->|Generate Content & Embeddings| AIProvider{LLM Providers\nOpenAI / Gemini / Groq}:::external
    Django <-->|Realtime RAG Chat| AIProvider
```

---

## Entity Relationship Diagram (ERD)

The database models isolate users by Workspaces, ensuring a secure multitenant SaaS environment.

```mermaid
erDiagram
    WORKSPACE {
        UUID id PK
        string name
        string llm_provider "openai, gemini, or groq"
        datetime created_at
    }

    USER {
        UUID id PK
        string username
        string email
        string password
        UUID workspace_id FK
    }

    DOCUMENT {
        UUID id PK
        string title
        string filename
        text extracted_text
        jsonb metadata
        string status "pending, processing, completed"
        UUID uploaded_by_id FK
        UUID workspace_id FK
    }

    DOCUMENT_CHUNK {
        UUID id PK
        text text
        vector embedding "1536 dimensions"
        UUID document_id FK
    }

    CHAT_HISTORY {
        UUID id PK
        text user_message
        text ai_response
        datetime created_at
        UUID user_id FK
        UUID document_id FK
    }

    WORKSPACE ||--|{ USER : "has many"
    WORKSPACE ||--|{ DOCUMENT : "has many"
    USER ||--|{ DOCUMENT : "uploads"
    DOCUMENT ||--|{ DOCUMENT_CHUNK : "split into"
    USER ||--|{ CHAT_HISTORY : "sends"
    DOCUMENT ||--|{ CHAT_HISTORY : "context for"
```

---

## Deployment Recommendations

The project is configured for deployment using standard Docker tools. 

- **Frontend (Next.js)**: Easily deployed on **Vercel** or Netlify by linking your GitHub repository and setting the build command to `npm run build` and output directory to `.next`.
- **Backend (Django/Celery)**: Easily deployed on **Render**, **Railway**, or **DigitalOcean App Platform** using the `Dockerfile` present in the backend directory.
- **Database**: A managed PostgreSQL database (such as **Supabase** or Render Managed Postgres) with the `pgvector` extension enabled is required.
