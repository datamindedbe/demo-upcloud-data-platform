from __future__ import annotations

import statistics

from benchmark.config import S3Config, BenchmarkParams
from benchmark.reader import read_big_file, read_small_files
from benchmark.writer import write_big_file, write_small_files

_BIG_FILE_KEY = "benchmark/big_file"
_SMALL_FILES_PREFIX = "benchmark/small"


def _summarise(results: list[dict], timing_key: str = "elapsed_s") -> dict:
    times = [r[timing_key] for r in results]
    return {
        "count": len(results),
        "total_s": sum(times),
        "mean_s": statistics.mean(times),
        "p50_s": statistics.median(times),
        "p99_s": sorted(times)[int(len(times) * 0.99)],
    }


def run_benchmark(config: S3Config, params: BenchmarkParams) -> dict:
    """Run all four benchmark scenarios and return a nested results dict."""
    results: dict = {}

    # --- writes ---
    results["write_big_file"] = write_big_file(
        config, _BIG_FILE_KEY, params.big_file_size_mb
    )

    small_write_results = write_small_files(
        config,
        _SMALL_FILES_PREFIX,
        params.small_file_count,
        params.small_file_size_kb,
        params.processes,
    )
    results["write_small_files"] = _summarise(small_write_results)

    # --- reads ---
    results["read_big_file"] = read_big_file(config, _BIG_FILE_KEY)

    small_keys = [r["key"] for r in small_write_results]
    results["read_small_files"] = _summarise(
        read_small_files(config, small_keys, params.processes)
    )

    return results
