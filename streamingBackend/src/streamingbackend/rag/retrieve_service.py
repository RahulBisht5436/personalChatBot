from streamingbackend.rag.config import TOP_K
from streamingbackend.rag.rag_store import get_vector_store
from streamingbackend.rag.resources_service import format_resource_context
from streamingbackend.utility.portfolio_context import BASE_ASSISTANT_INSTRUCTIONS


def retrieve_career_context(query: str, top_k: int = TOP_K) -> str:
    store = get_vector_store()
    results = store.similarity_search(query, k=top_k)
    resource_context = format_resource_context(query)

    if not results and not resource_context:
        return (
            f"{BASE_ASSISTANT_INSTRUCTIONS}\n\n"
            "No matching career documents were found in the knowledge base yet. "
            "Tell the visitor that this detail is not available until documents are ingested."
        )

    sections = [BASE_ASSISTANT_INSTRUCTIONS]

    if results:
        context_blocks = []
        for index, document in enumerate(results, start=1):
            source = document.metadata.get("file_name", "unknown")
            context_blocks.append(
                f"[Source {index}: {source}]\n{document.page_content.strip()}"
            )
        sections.append(
            "Use ONLY the career knowledge below when answering. "
            "If the answer is not present, say you do not have that detail yet.\n\n"
            + "\n\n".join(context_blocks)
        )

    if resource_context:
        sections.append(resource_context)

    sections.append(
        "When sharing a resume, PDF, or project, always include the markdown link from above. "
        "Use format: [Link label](url)."
    )

    return "\n\n".join(sections)
