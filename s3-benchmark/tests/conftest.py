from __future__ import annotations

import os
import time
import uuid

import boto3
import pytest
from botocore.config import Config

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
TEST_REGION = "us-east-1"


def _make_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=TEST_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(s3={"addressing_style": "path"}),
    )


def _wait_for_localstack(timeout: int = 60) -> None:
    import urllib.error
    import urllib.request

    health_url = f"{LOCALSTACK_ENDPOINT}/_localstack/health"
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            urllib.request.urlopen(health_url, timeout=3)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(2)

    raise RuntimeError(
        f"LocalStack not available at {LOCALSTACK_ENDPOINT} after {timeout}s: {last_error}"
    )


@pytest.fixture(scope="session")
def s3_client():
    _wait_for_localstack()
    return _make_s3_client()


@pytest.fixture()
def test_bucket(s3_client):
    bucket_name = f"test-{uuid.uuid4().hex[:8]}"
    # us-east-1 does not accept CreateBucketConfiguration
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name

    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture()
def s3_config(test_bucket):
    from benchmark.config import S3Config

    return S3Config(
        endpoint_url=LOCALSTACK_ENDPOINT,
        bucket=test_bucket,
        region=TEST_REGION,
    )
