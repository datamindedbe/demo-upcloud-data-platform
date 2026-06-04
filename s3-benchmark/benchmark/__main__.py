from __future__ import annotations

import argparse
import json

from benchmark.config import BenchmarkParams, S3Config
from benchmark.runner import run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="S3 benchmark tool")
    parser.add_argument("--endpoint-url", default="http://localhost:4566")
    parser.add_argument("--bucket", default="benchmark")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--big-file-size-mb", type=int, default=100)
    parser.add_argument("--small-file-size-kb", type=int, default=10)
    parser.add_argument("--small-file-count", type=int, default=100)
    parser.add_argument("--processes", type=int, default=4)
    args = parser.parse_args()

    config = S3Config(
        endpoint_url=args.endpoint_url,
        bucket=args.bucket,
        region=args.region,
    )
    params = BenchmarkParams(
        big_file_size_mb=args.big_file_size_mb,
        small_file_size_kb=args.small_file_size_kb,
        small_file_count=args.small_file_count,
        processes=args.processes,
    )

    results = run_benchmark(config, params)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
