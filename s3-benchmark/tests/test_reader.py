from benchmark.reader import read_big_file, read_small_files
from benchmark.writer import write_big_file, write_small_files


def test_read_big_file(s3_config, s3_client):
    key = "test/big_file"
    write_big_file(s3_config, key, size_mb=1)

    result = read_big_file(s3_config, key)

    assert result["key"] == key
    assert result["size_bytes"] == 1 * 1024 * 1024
    assert result["elapsed_s"] > 0


def test_read_small_files(s3_config, s3_client):
    write_results = write_small_files(
        s3_config, "test/small", count=5, size_kb=1, processes=2
    )
    keys = [r["key"] for r in write_results]

    results = read_small_files(s3_config, keys, processes=2)

    assert len(results) == 5
    for r in results:
        assert r["size_bytes"] == 1 * 1024
        assert r["elapsed_s"] > 0
