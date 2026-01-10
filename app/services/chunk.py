import tiktoken
from typing import List

import app.config as config


# Initialize tokenizer once (global, reused)
_encoder = tiktoken.get_encoding(config.TOKEN_ENCODING)


def chunk_text(
    text: str,
    max_tokens: int | None = None,
) -> List[str]:
    """
    Split text into token-based chunks.

    Args:
        text (str): Input text
        max_tokens (int | None): Override token limit per chunk

    Returns:
        List[str]: Clean text chunks
    """

    if not text or not isinstance(text, str):
        return []

    token_limit = max_tokens or config.CHUNK_TOKEN_SIZE
    if len(text) > 500_000:
        text = text[:500_000]

    tokens = _encoder.encode(text)
    chunks: List[str] = []

    overlap = int(token_limit * 0.15)

    for i in range(0, len(tokens), token_limit - overlap):

        chunk = _encoder.decode(tokens[i : i + token_limit])

        # Prevent useless tiny chunks
        if len(chunk.strip()) >= 50:
            chunks.append(chunk)

    return chunks
