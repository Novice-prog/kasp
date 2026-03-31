from app.utils.cleanup import cleanup_results


def test_cleanup_results_deletes_old_files(tmp_path):
    old_file = tmp_path / "old.xlsx"
    old_file.write_text("x")

    cleanup_results(folder=str(tmp_path), ttl_second=-1)

    assert not old_file.exists()


def test_cleanup_results_keeps_recent_files(tmp_path):
    fresh_file = tmp_path / "fresh.xlsx"
    fresh_file.write_text("x")

    cleanup_results(folder=str(tmp_path), ttl_second=3600)

    assert fresh_file.exists()
