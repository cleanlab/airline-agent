import argparse
import json

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding  # type: ignore[import-untyped]

from airline_agent.constants import RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE, RAG_EMBED_BATCH_SIZE, RAG_EMBED_MODEL
from airline_agent.types.knowledge_base import KBEntry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, help="Path to the JSON file with FAQs", required=True)
    parser.add_argument("--vector-db-path", type=str, help="Path to save the vector database", required=True)
    args = parser.parse_args()

    with open(args.data_path) as f:
        data: list[KBEntry] = [KBEntry(**entry) for entry in json.load(f)]

    documents = to_documents(data)

    index = create_index(documents)

    save_index(index, args.vector_db_path)


def to_documents(data: list[KBEntry]) -> list[Document]:
    documents: list[Document] = []
    for entry in data:
        doc = Document(
            text=entry.content,
            metadata={
                "path": entry.path,
                "title": entry.metadata.title,
            },
        )
        documents.append(doc)
    return documents


def create_index(documents: list[Document]) -> VectorStoreIndex:
    splitter = SentenceSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
    return VectorStoreIndex.from_documents(
        documents,
        transformations=[splitter],
        embed_model=OpenAIEmbedding(model_name=RAG_EMBED_MODEL, embed_batch_size=RAG_EMBED_BATCH_SIZE),
    )


def save_index(index: VectorStoreIndex, path: str) -> None:
    index.storage_context.persist(persist_dir=path)


if __name__ == "__main__":
    main()
