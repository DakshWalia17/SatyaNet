"""
Cryptographic hashing for chain-of-custody. Section 65B certificates require
the SHA-256 of the media both before and after any processing, so evidence
integrity can be independently verified in court.
"""
import hashlib


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
