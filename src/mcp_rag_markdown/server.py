import os
import httpx
from mcp.server.fastmcp import FastMCP

RAG_ENDPOINT = os.environ.get("RAG_ENDPOINT", "http://localhost:8090")

mcp = FastMCP(
    "rag-markdown",
    instructions="Semantic search over a markdown knowledge base via RAG",
)


@mcp.tool()
async def query_vault(query: str, top_k: int = 5) -> str:
    """Search the knowledge base using semantic similarity.

    Args:
        query: Natural language question to search for
        top_k: Number of results to return (default 5)

    Returns:
        Matching document chunks with source files and relevance scores
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                f"{RAG_ENDPOINT}/query",
                json={"q": query, "top_k": top_k},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError:
            return "RAG server unreachable. Check that the server is running."
        except httpx.HTTPStatusError as e:
            return f"RAG server error: {e.response.status_code}"

    if not data.get("results"):
        return "No results found."

    results = data["results"]
    max_score = max(r.get("score", 0) for r in results)

    if max_score < 0.50:
        return (
            "⚠️ No relevant results found (best score: "
            f"{max_score:.2f}, threshold: 0.50). "
            "The vault may not contain information on this topic."
        )

    lines = []
    for r in results:
        score = r.get("score", 0)
        source = r.get("source", "?")
        text = r.get("text", "").strip()
        confidence = "🟢" if score >= 0.60 else "🟡" if score >= 0.50 else "🔴"
        lines.append(f"**{confidence} [{score:.2f}] {source}**\n{text}\n")

    header = ""
    if max_score < 0.60:
        header = "⚠️ LOW CONFIDENCE — All results below 0.60. Use with caution.\n\n"

    return header + "\n---\n".join(lines)


@mcp.tool()
async def reindex_vault() -> str:
    """Trigger a re-indexation of the knowledge base.

    Use this after documents have been added or modified in the vault.

    Returns:
        Status of the re-indexation
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(f"{RAG_ENDPOINT}/reindex")
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError:
            return "RAG server unreachable."
        except httpx.HTTPStatusError as e:
            return f"RAG server error: {e.response.status_code}"

    if data.get("status") == "ok":
        return f"Re-indexation successful.\n{data.get('stdout', '')}"
    return f"Re-indexation failed.\n{data.get('stderr', '')}"


@mcp.tool()
async def vault_health() -> str:
    """Check the health status of the RAG server.

    Returns:
        Server status and number of indexed documents
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{RAG_ENDPOINT}/health")
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError:
            return "RAG server unreachable."
        except httpx.HTTPStatusError as e:
            return f"RAG server error: {e.response.status_code}"

    return f"Status: {data.get('status', '?')} — {data.get('documents_indexed', '?')} documents indexed"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
