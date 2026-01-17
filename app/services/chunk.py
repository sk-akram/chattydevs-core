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

    def _is_heading_line(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        if s.startswith("#"):
            return True
        if len(s) <= 80 and s.endswith(":"):
            return True
        if len(s) <= 60 and s.upper() == s and any(c.isalpha() for c in s):
            return True
        return False

    def _blocks(raw: str) -> List[str]:
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        lines = raw.split("\n")

        blocks: List[str] = []
        buf: List[str] = []
        in_code = False

        for line in lines:
            l = line.rstrip("\n")
            stripped = l.strip()

            if stripped.startswith("```"):
                if buf:
                    blocks.append("\n".join(buf).strip())
                    buf = []
                in_code = not in_code
                buf.append(l)
                continue

            if in_code:
                buf.append(l)
                continue

            if _is_heading_line(l) and buf:
                blocks.append("\n".join(buf).strip())
                buf = [l]
                continue

            if stripped == "":
                if buf:
                    blocks.append("\n".join(buf).strip())
                    buf = []
                continue

            buf.append(l)

        if buf:
            blocks.append("\n".join(buf).strip())

        return [b for b in blocks if b and len(b.strip()) >= 1]

    def _token_count(s: str) -> int:
        return len(_encoder.encode(s))

    overlap_tokens = int(token_limit * 0.15)
    min_chunk_chars = 50

    blocks = _blocks(text)
    if not blocks:
        return []

    chunks: List[str] = []
    prefix = ""
    current_parts: List[str] = []

    def _flush_current() -> None:
        nonlocal prefix, current_parts
        if not current_parts:
            return
        assembled = "\n\n".join([p for p in current_parts if p.strip()]).strip()
        if len(assembled) < min_chunk_chars:
            current_parts = []
            prefix = ""
            return
        chunks.append(assembled)

        if overlap_tokens > 0:
            t = _encoder.encode(assembled)
            if t:
                prefix = _encoder.decode(t[max(0, len(t) - overlap_tokens) :]).strip()
            else:
                prefix = ""
        else:
            prefix = ""
        current_parts = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        base_parts = []
        if not current_parts and prefix:
            base_parts.append(prefix)
        base_parts.extend(current_parts)
        base_parts.append(block)

        candidate = "\n\n".join([p for p in base_parts if p.strip()]).strip()
        if _token_count(candidate) <= token_limit:
            if not current_parts and prefix:
                current_parts.append(prefix)
            current_parts.append(block)
            continue

        if current_parts:
            _flush_current()

            base_parts = []
            if prefix:
                base_parts.append(prefix)
            base_parts.append(block)
            candidate = "\n\n".join([p for p in base_parts if p.strip()]).strip()
            if _token_count(candidate) <= token_limit:
                if prefix:
                    current_parts.append(prefix)
                current_parts.append(block)
                continue

        tokens = _encoder.encode(block)
        if not tokens:
            continue

        step = max(1, token_limit - overlap_tokens)
        for i in range(0, len(tokens), step):
            piece = _encoder.decode(tokens[i : i + token_limit]).strip()
            if len(piece) >= min_chunk_chars:
                chunks.append(piece)
        prefix = ""
        current_parts = []

    _flush_current()

    return chunks
