#!/usr/bin/env python3
"""
Ingest raw CSV files from S3 into Lakekeeper as Iceberg tables.

Usage:
    python ingest.py

Required env vars:
    AWS_S3_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    LAKEKEEPER_URL, LAKEKEEPER_WAREHOUSE (default: iceberg)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import upcloud_fileio  # noqa: F401 — patches PyIceberg's S3 factory for UpCloud

import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.fs as pa_fs
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError
from pyiceberg.io.pyarrow import pyarrow_to_schema

BUCKET = "dp-data-bucket"
RAW_PREFIX = "raw"
NAMESPACE = "demo"
TABLES = ["patients", "encounters", "conditions", "medications"]


def _s3_url() -> str:
    raw = os.environ.get("AWS_S3_ENDPOINT", "irp8o.upcloudobjects.com")
    return raw if raw.startswith(("http://", "https://")) else f"https://{raw}"


def s3_filesystem():
    # PyArrow endpoint_override expects host[:port] without scheme.
    host = _s3_url().removeprefix("https://").removeprefix("http://")
    return pa_fs.S3FileSystem(
        access_key=os.environ["AWS_ACCESS_KEY_ID"],
        secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        endpoint_override=host,
        region=os.environ.get("AWS_DEFAULT_REGION", "europe-1"),
    )


def catalog():
    return load_catalog(
        "lakekeeper",
        **{
            "type": "rest",
            "uri": os.environ.get("LAKEKEEPER_URL", "https://lakekeeper.upcloud.playground.dataminded.cloud/catalog/"),
            "warehouse": os.environ.get("LAKEKEEPER_WAREHOUSE", "iceberg"),
            "s3.endpoint": _s3_url(),
            "s3.access-key-id": os.environ["AWS_ACCESS_KEY_ID"],
            "s3.secret-access-key": os.environ["AWS_SECRET_ACCESS_KEY"],
            "s3.region": os.environ.get("AWS_DEFAULT_REGION", "europe-1"),
            "s3.path-style-access": "true",
            "auth": {
                "type": "oauth2",
                "oauth2": {
                    "client_id": "",
                    "client_secret": "",
                    "token_url": "https://zitadel.upcloud.playground.dataminded.cloud/oauth/v2/token",
                    "scope": "openid"
                }
            }
        },
    )


def _coerce_null_columns(table: pa.Table) -> pa.Table:
    # PyArrow infers pa.null() for fully-empty CSV columns; Iceberg v2 rejects
    # that type. Cast those columns to string so every field has a concrete type.
    for i, field in enumerate(table.schema):
        if pa.types.is_null(field.type):
            table = table.set_column(i, field.name, table.column(i).cast(pa.string()))
    return table


def _iceberg_schema(arrow_schema: pa.Schema):
    # pyarrow_to_schema requires PARQUET:field_id metadata on every field.
    # CSV-read schemas have none, so we stamp sequential IDs before converting.
    fields = [
        field.with_metadata({b"PARQUET:field_id": str(i + 1).encode()})
        for i, field in enumerate(arrow_schema)
    ]
    return pyarrow_to_schema(pa.schema(fields))


def ingest_table(fs, cat, table_name):
    path = f"{BUCKET}/{RAW_PREFIX}/{table_name}.csv"
    with fs.open_input_file(path) as f:
        arrow_table = pa_csv.read_csv(f)
    arrow_table = _coerce_null_columns(arrow_table)

    identifier = (NAMESPACE, f"raw_{table_name}")
    try:
        tbl = cat.load_table(identifier)
        tbl.overwrite(arrow_table)
        action = "overwritten"
    except NoSuchTableError:
        tbl = cat.create_table(identifier, schema=_iceberg_schema(arrow_table.schema))
        tbl.append(arrow_table)
        action = "created"

    print(f"  {action}: {NAMESPACE}.raw_{table_name} ({len(arrow_table):,} rows)")


def main():
    fs = s3_filesystem()
    cat = catalog()

    try:
        cat.create_namespace(NAMESPACE)
        print(f"created namespace '{NAMESPACE}'")
    except NamespaceAlreadyExistsError:
        pass

    for table_name in TABLES:
        print(f"ingesting {table_name}...")
        ingest_table(fs, cat, table_name)

    print("ingestion complete.")


if __name__ == "__main__":
    main()
