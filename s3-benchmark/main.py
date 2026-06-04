"""
Standalone benchmark script — runs six S3 scenarios and prints a results table.

Usage:
    uv run python main.py [--endpoint-url URL] [--bucket NAME]
                          [--big-file-size-mb MB] [--small-file-count N]
                          [--processes N]

Standard AWS / localstack auth (env vars, IAM roles):
    S3_ENDPOINT_URL, S3_BUCKET, AWS_DEFAULT_REGION,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

STS / OIDC proxy auth (e.g. s3sentinel reverse proxy):
    KEYCLOAK_URL, STS_ENDPOINT_URL, OIDC_USERNAME, OIDC_PASSWORD,
    OIDC_CLIENT_ID, ROLE_ARN
    (all can also be passed as CLI flags — see --help)

LocalStack:
    docker compose up -d && uv run python main.py

Real AWS S3:
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... S3_BUCKET=my-bucket \\
        uv run python main.py --big-file-size-mb 100 --small-file-count 1000

S3 proxy with STS auth:
    uv run python main.py \\
        --endpoint-url http://proxy:8080 \\
        --sts-endpoint http://sts:8090 \\
        --keycloak-url http://keycloak:8180/realms/s3sentinel/protocol/openid-connect/token \\
        --oidc-username admin --oidc-password admin123
"""

from __future__ import annotations

import argparse
import os
import socket
import statistics
import time
import uuid

from dotenv import load_dotenv

load_dotenv()  # load .env for local dev; never overrides already-set env vars

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from benchmark.config import S3Config, STSAuth
from benchmark.deleter import delete_file, delete_files
from benchmark.reader import list_files, read_big_file, read_small_files
from benchmark.writer import write_big_file, write_small_files

BIG_FILE_KEY = "benchmark/big_file"
SMALL_PREFIX = "benchmark/small"

console = Console()


def _make_client(config: S3Config):
    return config.make_client()


def _ensure_bucket(client, bucket: str) -> None:
    existing = {b["Name"] for b in client.list_buckets().get("Buckets", [])}
    if bucket not in existing:
        client.create_bucket(Bucket=bucket)
        console.print(f"  [dim]Created bucket [bold]{bucket}[/bold][/dim]")
    else:
        console.print(f"  [dim]Reusing bucket [bold]{bucket}[/bold][/dim]")


def _results_table(
    write_big: dict,
    write_big_wall_s: float,
    write_small: list[dict],
    write_small_wall_s: float,
    read_big: dict,
    read_big_wall_s: float,
    read_small: list[dict],
    read_small_wall_s: float,
    list_result: dict,
    list_wall_s: float,
    delete_big: dict,
    delete_big_wall_s: float,
    delete_small: list[dict],
    delete_small_wall_s: float,
    big_file_size_mb: int,
    small_file_count: int,
) -> Table:
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Operation")
    table.add_column("Count", justify="right")
    table.add_column("Total size", justify="right")
    table.add_column("Wall time (s)", justify="right")
    table.add_column("Avg per op (ms)", justify="right")
    table.add_column("Throughput", justify="right", style="green")

    def _mb(n: int) -> str:
        return f"{n} MB" if n >= 1 else f"{n * 1024} KB"

    # write big file
    table.add_row(
        "Write  big file",
        "1",
        _mb(big_file_size_mb),
        f"{write_big_wall_s:.3f}",
        f"{write_big_wall_s * 1000:.1f}",
        f"{big_file_size_mb / write_big_wall_s:.1f} MB/s",
    )

    # write small files
    avg_ms = statistics.mean(r["elapsed_s"] for r in write_small) * 1000
    table.add_row(
        "Write  small files",
        str(small_file_count),
        f"{small_file_count} KB",
        f"{write_small_wall_s:.3f}",
        f"{avg_ms:.1f}",
        f"{small_file_count / write_small_wall_s:.1f} files/s",
    )

    # read big file
    table.add_row(
        "Read   big file",
        "1",
        _mb(big_file_size_mb),
        f"{read_big_wall_s:.3f}",
        f"{read_big_wall_s * 1000:.1f}",
        f"{big_file_size_mb / read_big_wall_s:.1f} MB/s",
    )

    # read small files
    avg_ms = statistics.mean(r["elapsed_s"] for r in read_small) * 1000
    table.add_row(
        "Read   small files",
        str(small_file_count),
        f"{small_file_count} KB",
        f"{read_small_wall_s:.3f}",
        f"{avg_ms:.1f}",
        f"{small_file_count / read_small_wall_s:.1f} files/s",
    )

    # list files
    table.add_row(
        "List   files",
        str(list_result["count"]),
        "—",
        f"{list_wall_s:.3f}",
        f"{list_wall_s * 1000:.1f}",
        f"{list_result['count'] / list_wall_s:.1f} objects/s",
    )

    # delete big file
    table.add_row(
        "Delete big file",
        "1",
        _mb(big_file_size_mb),
        f"{delete_big_wall_s:.3f}",
        f"{delete_big_wall_s * 1000:.1f}",
        f"{big_file_size_mb / delete_big_wall_s:.1f} MB/s",
    )

    # delete small files
    avg_ms = statistics.mean(r["elapsed_s"] for r in delete_small) * 1000
    table.add_row(
        "Delete small files",
        str(small_file_count),
        f"{small_file_count} KB",
        f"{delete_small_wall_s:.3f}",
        f"{avg_ms:.1f}",
        f"{small_file_count / delete_small_wall_s:.1f} files/s",
    )

    return table


def run(
    config: S3Config,
    big_file_size_mb: int = 1,
    small_file_count: int = 5,
    processes: int = 2,
) -> None:
    client = _make_client(config)

    console.print(
        Panel.fit(
            f"[bold]S3 Benchmark[/bold]\n"
            f"Host      : [cyan]{socket.gethostname()}[/cyan]\n"
            f"Endpoint  : [cyan]{config.endpoint_url}[/cyan]\n"
            f"Bucket    : [cyan]{config.bucket}[/cyan]\n"
            f"Big file  : [cyan]{big_file_size_mb} MB[/cyan]\n"
            f"Small files: [cyan]{small_file_count} × 1 KB[/cyan]  "
            f"Workers: [cyan]{processes}[/cyan]",
            border_style="bright_blue",
        )
    )
    _ensure_bucket(client, config.bucket)
    console.print()

    write_big_result = write_small_results = read_big_result = read_small_results = (
        list_result
    ) = delete_big_result = delete_small_results = None
    write_big_wall = write_small_wall = read_big_wall = read_small_wall = list_wall = (
        delete_big_wall
    ) = delete_small_wall = 0.0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        t = progress.add_task(f"Writing big file  ({big_file_size_mb} MB)…", total=None)
        t0 = time.perf_counter()
        write_big_result = write_big_file(
            config, BIG_FILE_KEY, size_mb=big_file_size_mb
        )
        write_big_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Write big file  ({big_file_size_mb} MB)",
        )

        t = progress.add_task(
            f"Writing {small_file_count} small files ({processes} workers)…", total=None
        )
        t0 = time.perf_counter()
        write_small_results = write_small_files(
            config, SMALL_PREFIX, count=small_file_count, size_kb=1, processes=processes
        )
        write_small_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Write {small_file_count} small files",
        )

        t = progress.add_task(f"Reading big file  ({big_file_size_mb} MB)…", total=None)
        t0 = time.perf_counter()
        read_big_result = read_big_file(config, BIG_FILE_KEY)
        read_big_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Read big file  ({big_file_size_mb} MB)",
        )

        t = progress.add_task(
            f"Reading {small_file_count} small files ({processes} workers)…", total=None
        )
        t0 = time.perf_counter()
        read_small_results = read_small_files(
            config, [r["key"] for r in write_small_results], processes=processes
        )
        read_small_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Read {small_file_count} small files",
        )

        t = progress.add_task(f"Listing files under {SMALL_PREFIX}/…", total=None)
        t0 = time.perf_counter()
        list_result = list_files(config, SMALL_PREFIX)
        list_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] List files ({list_result['count']} objects)",
        )

        t = progress.add_task(
            f"Deleting big file  ({big_file_size_mb} MB)…", total=None
        )
        t0 = time.perf_counter()
        delete_big_result = delete_file(config, BIG_FILE_KEY)
        delete_big_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Delete big file  ({big_file_size_mb} MB)",
        )

        t = progress.add_task(
            f"Deleting {small_file_count} small files ({processes} workers)…",
            total=None,
        )
        t0 = time.perf_counter()
        delete_small_results = delete_files(
            config, [r["key"] for r in write_small_results], processes=processes
        )
        delete_small_wall = time.perf_counter() - t0
        progress.update(
            t,
            total=1,
            completed=1,
            description=f"[green]✓[/green] Delete {small_file_count} small files",
        )

    console.print()
    console.print(
        _results_table(
            write_big_result,
            write_big_wall,
            write_small_results,
            write_small_wall,
            read_big_result,
            read_big_wall,
            read_small_results,
            read_small_wall,
            list_result,
            list_wall,
            delete_big_result,
            delete_big_wall,
            delete_small_results,
            delete_small_wall,
            big_file_size_mb,
            small_file_count,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="S3 benchmark",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        help="S3 endpoint URL (env: S3_ENDPOINT_URL). Omit for real AWS S3.",
    )
    parser.add_argument(
        "--bucket",
        default=os.getenv("S3_BUCKET", f"benchmark-{uuid.uuid4().hex[:8]}"),
        help="Bucket name — created if absent (env: S3_BUCKET).",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        help="AWS region (env: AWS_DEFAULT_REGION).",
    )
    parser.add_argument(
        "--big-file-size-mb",
        type=int,
        default=int(os.getenv("BIG_FILE_SIZE_MB", "1")),
        metavar="MB",
        help="Size of the big file (env: BIG_FILE_SIZE_MB).",
    )
    parser.add_argument(
        "--small-file-count",
        type=int,
        default=int(os.getenv("SMALL_FILE_COUNT", "5")),
        metavar="N",
        help="Number of 1 KB small files (env: SMALL_FILE_COUNT).",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=int(os.getenv("PROCESSES", "2")),
        metavar="N",
        help="Parallel workers for small-file operations (env: PROCESSES).",
    )

    sts = parser.add_argument_group(
        "STS / OIDC auth",
        "Use when the S3 endpoint is a proxy that requires JWT session tokens. "
        "All args also readable from env vars.",
    )
    sts.add_argument(
        "--keycloak-url",
        default=os.getenv("KEYCLOAK_URL"),
        help="Keycloak token endpoint (env: KEYCLOAK_URL).",
    )
    sts.add_argument(
        "--sts-endpoint",
        default=os.getenv("STS_ENDPOINT_URL"),
        help="STS endpoint for AssumeRoleWithWebIdentity (env: STS_ENDPOINT_URL).",
    )
    sts.add_argument(
        "--oidc-username",
        default=os.getenv("OIDC_USERNAME"),
        help="OIDC username (env: OIDC_USERNAME).",
    )
    sts.add_argument(
        "--oidc-password",
        default=os.getenv("OIDC_PASSWORD"),
        help="OIDC password (env: OIDC_PASSWORD).",
    )
    sts.add_argument(
        "--oidc-client-id",
        default=os.getenv("OIDC_CLIENT_ID", "s3sentinel"),
        help="OIDC client ID (env: OIDC_CLIENT_ID).",
    )
    sts.add_argument(
        "--role-arn",
        default=os.getenv("ROLE_ARN", "arn:aws:iam::000000000000:role/s3sentinel"),
        help="Role ARN for AssumeRoleWithWebIdentity (env: ROLE_ARN).",
    )

    args = parser.parse_args()

    sts_auth = None
    if (
        args.keycloak_url
        and args.sts_endpoint
        and args.oidc_username
        and args.oidc_password
    ):
        sts_auth = STSAuth(
            keycloak_url=args.keycloak_url,
            sts_endpoint=args.sts_endpoint,
            username=args.oidc_username,
            password=args.oidc_password,
            client_id=args.oidc_client_id,
            role_arn=args.role_arn,
        )

    endpoint_url = (
        args.endpoint_url
        or os.getenv("S3_ENDPOINT_URL")
        or os.getenv("LOCALSTACK_ENDPOINT")
    )

    if sts_auth:
        console.print("[dim]Resolving STS credentials via Keycloak…[/dim]")
        config = S3Config.from_sts(
            bucket=args.bucket,
            endpoint_url=endpoint_url,
            region=args.region,
            sts_auth=sts_auth,
        )
    else:
        config = S3Config(
            bucket=args.bucket,
            region=args.region,
            **({"endpoint_url": endpoint_url} if endpoint_url else {}),
        )
    run(
        config,
        big_file_size_mb=args.big_file_size_mb,
        small_file_count=args.small_file_count,
        processes=args.processes,
    )


if __name__ == "__main__":
    main()
