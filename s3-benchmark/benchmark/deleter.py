from __future__ import annotations

import time

from benchmark.config import S3Config
from canal.flow import map_async


def _make_client(config: S3Config):
    """Create a boto3 S3 client. Always call this inside the worker process."""
    return config.make_client()


def delete_file(config: S3Config, key: str) -> dict:
    """Delete a single object and return timing info."""
    client = _make_client(config)

    start = time.perf_counter()
    client.delete_object(Bucket=config.bucket, Key=key)
    elapsed = time.perf_counter() - start

    return {"key": key, "elapsed_s": elapsed}


def delete_files(
    config: S3Config,
    keys: list[str],
    processes: int = 4,
) -> list[dict]:
    """Delete many objects in parallel and return per-file timing info."""
    def _delete(key: str) -> dict:
        # Client created inside the worker to be fork-safe.
        client = _make_client(config)

        start = time.perf_counter()
        client.delete_object(Bucket=config.bucket, Key=key)
        elapsed = time.perf_counter() - start

        return {"key": key, "elapsed_s": elapsed}

    return list(map_async(_delete, iter(keys), processes=processes))
