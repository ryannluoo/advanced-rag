from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, model_validator
from transformers import AutoTokenizer

_MAX_OVERLAP_PERCENT = 30


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(
        default=384,
        ge=32,
        le=2048,
        description="The size of the chunk to create"
    )
    chunk_overlap: int = Field(
        default=64,
        ge=0,
        description="The overlap between chunks"
    )
    tokenizer_model: str = Field(
        default="Qwen/Qwen3-Embedding-0.6B",
        description="The tokenizer model to use"
    )

    @model_validator(mode="after")
    def validate_chunk_overlap(self) -> "ChunkingConfig":
        if self.chunk_overlap > self.chunk_size * _MAX_OVERLAP_PERCENT // 100:
            raise ValueError(
                f"Chunk overlap {self.chunk_overlap} is greater than {_MAX_OVERLAP_PERCENT}% of chunk size {self.chunk_size}"
            )
        return self


class RecursiveTokenChunker:
    def __init__(self, config: ChunkingConfig):
        self.config = config

        self._tokenizer = AutoTokenizer.from_pretrained(
            config.tokenizer_model,
            trust_remote_code=True
        )

        self._splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self._tokenizer,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", " ", ""],
            keep_separator="end"
        )

    def chunk_report(self, report: dict) -> list[dict]:
        """Split rendered pages independently, preserving source character offsets.

        Chunk indexes are zero-based within each page. Character offsets use
        Python string indexing, with an inclusive start and exclusive end.
        Token counts exclude special tokens.
        """
        document_id = report["metadata"]["document_id"]
        chunks = []
        for page in report["pages"]:
            page_number = page["page"]
            page_text = page["text"]
            search_start = 0
            previous_end = 0
            page_chunks = self._splitter.split_text(page_text)
            for chunk_index, text in enumerate(page_chunks):
                # Search forwards while allowing overlap. Token overlap cannot
                # be subtracted from a character offset. Repeated table cells
                # must not match an earlier occurrence inside the last chunk.
                search_start = max(search_start, previous_end - len(text))
                char_start = page_text.find(text, search_start)
                if chunk_index == len(page_chunks) - 1:
                    # Anchor the final chunk to the end, including pages whose
                    # last chunk is only a repeated table delimiter.
                    char_start = page_text.rfind(text, search_start)
                while char_start != -1 and char_start < previous_end:
                    overlap_tokens = len(self._tokenizer.tokenize(
                        page_text[char_start:previous_end]
                    ))
                    if overlap_tokens <= self.config.chunk_overlap:
                        break
                    char_start = page_text.find(text, char_start + 1)
                if char_start == -1:
                    raise ValueError(
                        f"Chunk {chunk_index} on page {page_number} of "
                        f"{document_id} could not be located in its source text"
                    )
                char_end = char_start + len(text)
                chunks.append({
                    "metadata": {
                        "chunk_id": f"{document_id}:p{page_number}:c{chunk_index}",
                        "document_id": document_id,
                        "page": page_number,
                        "chunk_index": chunk_index,
                        "token_count": len(self._tokenizer.encode(
                            text, add_special_tokens=False
                        )),
                        "char_start": char_start,
                        "char_end": char_end,
                    },
                    "text": text,
                })
                search_start = char_start + 1
                previous_end = char_end
        return chunks
