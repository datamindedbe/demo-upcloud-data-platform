"""
Patches PyIceberg's S3 filesystem factory for UpCloud Object Storage.

Import this module before calling load_catalog() to activate the patch.

WHY a module-level patch instead of py-io-impl / subclassing:
  The REST catalog merges table_response.config (from the server) on top of
  the local catalog properties, so any py-io-impl we set can be silently
  overridden by Lakekeeper.  Patching SCHEME_TO_FS at the Python module level
  means every FsspecFileIO instance created afterwards picks up our factory,
  regardless of where the FileIO class comes from.

WHAT we fix:
  - Path-style addressing: UpCloud rejects virtual-host URLs.
  - request_checksum_calculation / response_checksum_validation = when_required:
    botocore ≥1.35 sends CRC32 flexible-checksum headers by default; UpCloud
    rejects PutObject with AccessDenied and UploadPart with
    XAmzContentSHA256Mismatch.
"""
import s3fs
import pyiceberg.io.fsspec as _fsspec


def _s3_for_upcloud(properties):
    client_kwargs = {}
    if endpoint := properties.get("s3.endpoint"):
        client_kwargs["endpoint_url"] = endpoint
    if region := properties.get("s3.region"):
        client_kwargs["region_name"] = region
    if key := properties.get("s3.access-key-id"):
        client_kwargs["aws_access_key_id"] = key
    if secret := properties.get("s3.secret-access-key"):
        client_kwargs["aws_secret_access_key"] = secret
    if token := properties.get("s3.session-token"):
        client_kwargs["aws_session_token"] = token

    path_style = properties.get("s3.path-style-access", "false").lower() == "true"
    return s3fs.S3FileSystem(
        client_kwargs=client_kwargs,
        config_kwargs={
            "s3": {"addressing_style": "path" if path_style else "virtual"},
            "request_checksum_calculation": "when_required",
            "response_checksum_validation": "when_required",
        },
    )


for _scheme in ("s3", "s3a", "s3n"):
    _fsspec.SCHEME_TO_FS[_scheme] = _s3_for_upcloud
