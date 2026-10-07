from dataclasses import dataclass, field
from io import BytesIO

from pypdf import PdfReader


@dataclass
class Document:
    page_content: str
    metadata: dict = field(default_factory=dict)


class DocumentHelper:
    @staticmethod
    def load_pdf(content: bytes, source: str) -> list[Document]:
        reader = PdfReader(BytesIO(content))
        return [
            Document(
                page_content=page.extract_text() or "",
                metadata={"source": source, "page": page_number},
            )
            for page_number, page in enumerate(reader.pages)
        ]

    @staticmethod
    def split_documents(documents, chunk_size: int = 500, chunk_overlap: int = 50):
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Invalid chunk size or overlap")

        chunks = []
        step = chunk_size - chunk_overlap
        for document in documents:
            text = document.page_content.strip()
            for start in range(0, len(text), step):
                chunk_text = text[start:start + chunk_size].strip()
                if chunk_text:
                    chunks.append(
                        Document(chunk_text, dict(document.metadata)))
        return chunks
