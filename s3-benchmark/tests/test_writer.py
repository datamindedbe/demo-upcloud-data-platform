from benchmark.writer import write_big_file, write_small_files


def test_write_big_file(s3_config, s3_client):
    key = "test/big_file"
    result = write_big_file(s3_config, key, size_mb=1)

    assert result["key"] == key
    assert result["size_mb"] == 1
    assert result["elapsed_s"] > 0

    head = s3_client.head_object(Bucket=s3_config.bucket, Key=key)
    assert head["ContentLength"] == 1 * 1024 * 1024


def test_write_small_files(s3_config, s3_client):
    results = write_small_files(s3_config, "test/small", count=5, size_kb=1, processes=2)

    assert len(results) == 5
    for r in results:
        assert r["size_kb"] == 1
        assert r["elapsed_s"] > 0
        head = s3_client.head_object(Bucket=s3_config.bucket, Key=r["key"])
        assert head["ContentLength"] == 1 * 1024
