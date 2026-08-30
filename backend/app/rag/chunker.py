from typing import List, Dict, Any

def chunk_text(
    text: str,
    source: str,
    role: str,
    chunk_size: int = 900,
    overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Paragraph-aware text chunking with overlap metadata.
    """
    if not text or not text.strip():
        return []

    # Split into double-newline separated paragraphs first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: List[Dict[str, Any]] = []
    current_chunk = ""
    chunk_index = 0

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            if current_chunk:
                chunks.append({
                    "text": current_chunk,
                    "metadata": {
                        "source": source,
                        "role": role,
                        "chunk_index": chunk_index
                    }
                })
                chunk_index += 1

                # Retain overlap from end of current chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + paragraph if overlap_text else paragraph
            else:
                # Paragraph itself exceeds chunk_size, hard break
                current_chunk = paragraph

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {
                "source": source,
                "role": role,
                "chunk_index": chunk_index
            }
        })

    return chunks
