# mcp-rag-markdown

MCP server for semantic search over markdown knowledge bases via RAG.

## Tools

- **query_vault** — Search the knowledge base using semantic similarity
- **reindex_vault** — Trigger a re-indexation of the knowledge base
- **vault_health** — Check the health status of the RAG server

## Requirements

A running RAG server (FastAPI) that provides `/query`, `/reindex`, and `/health` endpoints.

Set `RAG_ENDPOINT` environment variable to point to your server (default: `http://localhost:8090`).

## Installation

```bash
pip install mcp-rag-markdown
```

## Usage with Claude Code

```json
{
  "mcpServers": {
    "rag-markdown": {
      "command": "mcp-rag-markdown",
      "env": {
        "RAG_ENDPOINT": "http://localhost:8090"
      }
    }
  }
}
```
