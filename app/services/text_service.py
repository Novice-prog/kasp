import re
from app.utils.normalizer import normalize_word


def process_text(file_path:str) -> dict:
    stats = {}

    with open(file_path, 'r', encoding="utf-8") as f:
        for line_index, line in enumerate(f):
            words = re.findall(r"[а-яё]+", line.lower())
            for word in words:
                normal_form = normalize_word(word)

                if normal_form not in stats:
                    stats[normal_form] = {
                        "total": 0,
                        "per_line": {}
                    }

                stats[normal_form]["total"] += 1
                stats[normal_form]["per_line"][line_index] = (
                    stats[normal_form]["per_line"].get(line_index, 0) + 1
                )

    return stats
