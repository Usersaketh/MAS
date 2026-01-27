# MAS Frontend

A modern React + TypeScript + Vite frontend for the Multi-Agent Support System.

## Features

- **Query Interface**: Submit customer questions with real-time processing
- **Response Display**: View agent responses with:
  - Intent classification & confidence
  - Escalation status
  - Retrieved context from FAISS
  - Execution traces and timelines
  - Conversation memory
- **Document Management**: Ingest and manage support documentation
- **Index Statistics**: Monitor FAISS index size and document count
- **Beautiful UI**: Clean, responsive design with dark mode ready

## Setup

```powershell
# Navigate to frontend directory
cd frontend

# Copy environment
Copy-Item .env.example .env

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at `http://localhost:3000` and proxy API calls to `http://localhost:8000`.

## Environment Variables

Create a `.env` file:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=dev-interview-key
```

## API Integration

The frontend communicates with the FastAPI backend via:

- `POST /query` – Process customer queries
- `POST /documents` – Ingest documents
- `GET /documents/stats` – Retrieve index statistics
- `GET /observability/conversations/{id}/memory` – View conversation history
- `GET /observability/conversations/{id}/traces` – View execution traces

All requests include the `X-API-Key` header automatically.

## Build

```powershell
npm run build
```

Outputs to `dist/`.

## Architecture

```
src/
├── api/
│   └── client.ts          # API client with type-safe methods
├── components/
│   ├── QueryForm.tsx      # Query input form
│   ├── ResponseDisplay.tsx # Response & trace display
│   ├── DocumentManager.tsx # Document ingestion
│   └── Stats.tsx          # Index statistics
├── App.tsx                # Main app component
├── App.module.css         # Global styles
├── main.tsx               # React entry point
└── index.css              # Base styles
```

## Styling

Uses CSS Modules for component-level styling with a clean, minimal design system:
- Primary color: `#4f46e5` (Indigo)
- Accents: Red (#ef4444), Green (#10b981), Blue (#0284c7)
- Responsive layout with mobile support

## Tips

1. Always start the backend before the frontend
2. Ingest sample documents first (use the UI or the provided seed script)
3. The conversation ID persists memory across queries within the same session
4. Each query execution shows full trace events with per-node durations
