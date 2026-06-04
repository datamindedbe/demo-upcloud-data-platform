from __future__ import annotations

import io
import time

from benchmark.config import S3Config
from canal.flow import map_async


def _make_client(config: S3Config):
    """Create a boto3 S3 client. Always call this inside the worker process."""
    return config.make_client()


def write_big_file(config: S3Config, key: str, size_mb: int = 100) -> dict:
    """Upload a single large file and return timing info."""
    client = _make_client(config)
    data = io.BytesIO(b"0" * size_mb * 1024 * 1024)

    start = time.perf_counter()
    client.upload_fileobj(data, config.bucket, key)
    elapsed = time.perf_counter() - start

    return {"key": key, "size_mb": size_mb, "elapsed_s": elapsed}


def write_small_files(
    config: S3Config,
    prefix: str,
    count: int,
    size_kb: int = 10,
    processes: int = 4,
) -> list[dict]:
    """Upload many small files in parallel and return per-file timing info."""

    def _upload(index: int) -> dict:
        # Client created inside the worker to be fork-safe.
        client = _make_client(config)
        key = f"{prefix}/{index:06d}"
        body = b"x" * size_kb * 1024

        start = time.perf_counter()
        client.put_object(Bucket=config.bucket, Key=key, Body=body)
        elapsed = time.perf_counter() - start

        return {"key": key, "size_kb": size_kb, "elapsed_s": elapsed}

    return list(map_async(_upload, iter(range(count)), processes=processes))
