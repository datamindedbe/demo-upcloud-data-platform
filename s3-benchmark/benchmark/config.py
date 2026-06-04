from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

import boto3
from botocore.config import Config


@dataclass
class STSAuth:
    """Credentials for the Keycloak → STS → temp-credentials flow.

    Used when the S3 endpoint is a reverse proxy that validates JWT session tokens
    (e.g. s3sentinel). Set all fields to enable; leave unset for standard AWS auth.
    """

    keycloak_url: str
    sts_endpoint: str
    username: str
    password: str
    client_id: str = "s3sentinel"
    role_arn: str = "arn:aws:iam::000000000000:role/s3sentinel"
    role_session_name: str = "benchmark"

    @classmethod
    def from_env(cls) -> STSAuth | None:
        """Return an STSAuth from env vars, or None if not configured."""
        keycloak_url = os.getenv("KEYCLOAK_URL")
        sts_endpoint = os.getenv("STS_ENDPOINT_URL")
        username = os.getenv("OIDC_USERNAME")
        password = os.getenv("OIDC_PASSWORD")
        if not all([keycloak_url, sts_endpoint, username, password]):
            return None
        return cls(
            keycloak_url=keycloak_url,
            sts_endpoint=sts_endpoint,
            username=username,
            password=password,
            client_id=os.getenv("OIDC_CLIENT_ID", "s3sentinel"),
            role_arn=os.getenv("ROLE_ARN", "arn:aws:iam::000000000000:role/s3sentinel"),
            role_session_name=os.getenv("ROLE_SESSION_NAME", "benchmark"),
        )

    def resolve(self) -> dict:
        """Fetch an OIDC token from Keycloak and exchange it for S3 credentials via STS.

        Returns a dict with AccessKeyId, SecretAccessKey, SessionToken.
        """
        jwt_token = self._get_jwt_token()
        return self._assume_role(jwt_token)

    def _get_jwt_token(self) -> str:
        data = urllib.parse.urlencode(
            {
                "grant_type": "password",
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
            }
        ).encode()
        with urllib.request.urlopen(self.keycloak_url, data) as r:
            return json.load(r)["access_token"]

    def _assume_role(self, jwt_token: str) -> dict:
        sts = boto3.client(
            "sts",
            endpoint_url=self.sts_endpoint,
            aws_access_key_id="placeholder",
            aws_secret_access_key="placeholder",
            region_name="us-east-1",
        )
        resp = sts.assume_role_with_web_identity(
            RoleArn=self.role_arn,
            RoleSessionName=self.role_session_name,
            WebIdentityToken=jwt_token,
        )
        return resp["Credentials"]


@dataclass
class S3Config:
    """Connection settings for an S3-compatible endpoint.

    Credentials follow standard boto3 precedence: explicit values here take
    priority, otherwise boto3 reads AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
    from the environment (compatible with K8s Secrets and IAM roles).

    Set endpoint_url=None to target real AWS S3.
    """

    bucket: str
    endpoint_url: str | None = field(default_factory=lambda: os.getenv("S3_ENDPOINT_URL") or os.getenv("LOCALSTACK_ENDPOINT"))  # None → real AWS S3
    region: str = field(default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    aws_access_key_id: str | None = field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID"))
    aws_secret_access_key: str | None = field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY"))
    aws_session_token: str | None = None  # populated from STS temp credentials

    @classmethod
    def from_sts(cls, bucket: str, endpoint_url: str, region: str, sts_auth: STSAuth) -> S3Config:
        """Build an S3Config by resolving credentials via the STS/OIDC flow."""
        creds = sts_auth.resolve()
        return cls(
            bucket=bucket,
            endpoint_url=endpoint_url,
            region=region,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

    def make_client(self):
        """Create a boto3 S3 client from this config.

        Always call inside the worker process — never share clients across forks.
        Uses path-style addressing for custom endpoints (localstack / MinIO),
        and virtual-hosted style for real AWS S3.
        """
        addressing = "path" if self.endpoint_url else "auto"
        s3_config: dict = {"addressing_style": addressing}
        extra: dict = {}
        if self.endpoint_url:
            # S3-compatible endpoints (UpCloud, localstack, MinIO) don't support
            # boto3's default payload signing / checksum behaviour; disable both.
            s3_config["payload_signing_enabled"] = False
            extra["request_checksum_calculation"] = "when_required"
            extra["response_checksum_validation"] = "when_required"
        kwargs: dict = dict(
            region_name=self.region,
            config=Config(s3=s3_config, **extra),
        )
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        if self.aws_access_key_id:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            kwargs["aws_session_token"] = self.aws_session_token
        return boto3.client("s3", **kwargs)


@dataclass
class BenchmarkParams:
    """Tuning knobs for a benchmark run."""

    big_file_size_mb: int = 100
    small_file_size_kb: int = 10
    small_file_count: int = 100
    processes: int = 4
