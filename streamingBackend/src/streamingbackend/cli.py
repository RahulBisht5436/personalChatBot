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
