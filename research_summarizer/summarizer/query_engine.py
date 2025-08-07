import argparse
from langchain_community.embeddings import OpenAIEmbeddings 
from langchain_community.vectorstores.chroma import Chroma



def query_the_data(query_text, paper_id, openai_api_key, k=5, relevance_threshold=0.5):
    chroma_path = 'chroma_db/'
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(
        query_text, k=k, filter={"paper_id": paper_id}
    )

    if not results:
        print("[WARN] No results returned by Chroma.")
        return query_text, None

    # Debug print relevance scores
    print("[DEBUG] Relevance scores:")
    for doc, score in results:
        print(f"  - {score:.3f} -> {doc.page_content[:80]}...")

    filtered = [(doc, score) for doc, score in results if score >= relevance_threshold]
    if not filtered:
        print(f"[INFO] All scores below threshold ({relevance_threshold})")
        return query_text, None

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in filtered])
    return query_text, context_text
