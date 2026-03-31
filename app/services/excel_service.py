from openpyxl import Workbook

EXCEL_CELL_CHAR_LIMIT = 32767


def _safe_cell_value(value: str) -> str:
    if len(value) <= EXCEL_CELL_CHAR_LIMIT:
        return value
    suffix = "...[TRUNCATED]"
    return value[: EXCEL_CELL_CHAR_LIMIT - len(suffix)] + suffix


def create_excel(stats: dict, output_path:str):
    wb = Workbook()
    ws = wb.active

    ws.append(["Слово", "Всего", "По строкам"])

    for word, data in stats.items():
        per_line_dict = data["per_line"]

        max_line = max(per_line_dict.keys(), default=0)

        per_line_list = [
            str(per_line_dict.get(i, 0))
            for i in range(max_line + 1)
        ]

        per_line_str = ",".join(per_line_list)

        ws.append([
            word,
            data["total"],
            _safe_cell_value(per_line_str)
        ])

    wb.save(output_path)
