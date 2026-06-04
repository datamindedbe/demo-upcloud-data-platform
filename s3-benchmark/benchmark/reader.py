from __future__ import annotations

import time

from canal.flow import map_async
from benchmark.config import S3Config


def _make_client(config: S3Config):
    """Create a boto3 S3 client. Always call this inside the worker process."""
    return config.make_client()


def read_big_file(config: S3Config, key: str) -> dict:
    """Download a single large file and return timing + size info."""
    client = _make_client(config)

    start = time.perf_counter()
    response = client.get_object(Bucket=config.bucket, Key=key)
    data = response["Body"].read()
    elapsed = time.perf_counter() - start

    return {"key": key, "size_bytes": len(data), "elapsed_s": elapsed}


def list_files(config: S3Config, prefix: str) -> dict:
    """List all objects under a prefix (handles pagination) and return timing + count."""
    client = _make_client(config)
    paginator = client.get_paginator("list_objects_v2")

    count = 0
    start = time.perf_counter()
    for page in paginator.paginate(Bucket=config.bucket, Prefix=prefix):
        count += len(page.get("Contents", []))
    elapsed = time.perf_counter() - start

    return {"prefix": prefix, "count": count, "elapsed_s": elapsed}


def read_small_files(
    config: S3Config,
    keys: list[str],
    processes: int = 4,
) -> list[dict]:
    """Download many small files in parallel and return per-file timing info."""

    def _download(key: str) -> dict:
        # Client created inside the worker to be fork-safe.
        client = _make_client(config)

        start = time.perf_counter()
        response = client.get_object(Bucket=config.bucket, Key=key)
        data = response["Body"].read()
        elapsed = time.perf_counter() - start

        return {"key": key, "size_bytes": len(data), "elapsed_s": elapsed}

    return list(map_async(_download, iter(keys), processes=processes))
