import argparse
import hashlib
import json
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding  # type: ignore[import-untyped]

from airline_agent.constants import RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE, RAG_EMBED_BATCH_SIZE, RAG_EMBED_MODEL
from airline_agent.types.knowledge_base import KBArticle


def main() -> None:
    load_dotenv()

    options = parse_args()

    project_root = Path(__file__).resolve().parents[3]
    data_path = project_root / "data" / "kb.json"
    vector_db_path = project_root / "data" / "vector-db"

    if not options.no_verify_checksum:
        verify_checksum(data_path)

    with data_path.open() as f:
        data: list[KBArticle] = [KBArticle(**entry) for entry in json.load(f)]

    documents = to_documents(data)

    index = create_index(documents)

    save_index(index, vector_db_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a vector database from the knowledge base.")
    parser.add_argument(
        "--no-verify-checksum", action="store_true", help="Skip checksum verification of the knowledge base file"
    )
    return parser.parse_args()


def to_documents(data: list[KBArticle]) -> list[Document]:
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


def save_index(index: VectorStoreIndex, path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(path))


def verify_checksum(file_path: Path) -> None:
    checksums_path = Path(__file__).resolve().parents[3] / "data" / "CHECKSUMS"
    if not file_path.exists():
        msg = f"Knowledge base file not found at {file_path}"
        raise FileNotFoundError(msg)
    if not checksums_path.exists():
        msg = f"Checksum file not found at {checksums_path}"
        raise FileNotFoundError(msg)

    expected = _lookup_expected_checksum(checksums_path, file_path.name)
    if expected is None:
        msg = f"No checksum entry found for {file_path.name} in {checksums_path}"
        raise ValueError(msg)

    actual = _calculate_sha256(file_path)
    if actual != expected:
        msg = f"Checksum mismatch for {file_path}. Expected {expected}, but found {actual}."
        raise ValueError(msg)


def _lookup_expected_checksum(checksums_path: Path, target_name: str) -> str | None:
    with checksums_path.open() as checksums_file:
        for line in checksums_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 2:  # noqa: PLR2004
                continue
            checksum, filename = parts[0], parts[-1]
            if Path(filename).name == target_name:
                return checksum
    return None


def _calculate_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
