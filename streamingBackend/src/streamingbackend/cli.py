def langgraph_dev() -> None:
    """Launch LangGraph dev server (Studio + in-memory agent server on :2024)."""
    import shutil
    import subprocess
    import sys
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parents[2]
    langgraph_cmd = shutil.which("langgraph")
    if langgraph_cmd is None:
        venv_langgraph = Path(sys.executable).with_name("langgraph.exe")
        if venv_langgraph.exists():
            langgraph_cmd = str(venv_langgraph)
        else:
            raise RuntimeError(
                "langgraph CLI not found. Run `uv sync` in streamingBackend first."
            )

    subprocess.run(
        [langgraph_cmd, "dev", "--config", "langgraph.json"],
        cwd=backend_dir,
        check=True,
    )


def serve() -> None:
    import uvicorn

    uvicorn.run(
        "streamingbackend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


def ingest_rag() -> None:
    from streamingbackend.rag.ingest_service import ingest_documents

    result = ingest_documents()
    print("RAG ingest complete:")
    print(f"  Ingested: {len(result['ingested'])}")
    print(f"  Skipped:  {len(result['skipped'])}")
    print(f"  Removed:  {len(result['removed'])}")
    print(f"  Failed:   {len(result['failed'])}")
    if result["failed"]:
        for item in result["failed"]:
            print(f"    - {item['file']}: {item['error']}")
