from app.services.text_service import process_text


def test_process_text_basic(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("житель\nжителем жителем")

    result = process_text(str(file))

    assert "житель" in result

    data = result["житель"]

    assert data["total"] == 3
    assert data["per_line"][0] == 1
    assert data["per_line"][1] == 2

def test_empty_file(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("")

    result = process_text(str(file))

    assert result == {}

def test_normalization(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("житель жителя жителем")

    result = process_text(str(file))

    assert "житель" in result
    assert result["житель"]["total"] == 3


def test_non_cyrillic_words_are_ignored(tmp_path):
    file = tmp_path / "mixed.txt"
    file.write_text("hello 123 !!!\nжитель")

    result = process_text(str(file))

    assert len(result) == 1
    assert result["житель"]["total"] == 1

