def parse_table(table, extractor):
    col_mapping = {}
    for i, heading in enumerate(table.thead.find_all('th')):
        col_mapping[i] = ''.join(heading.stripped_strings)
    rows = []
    for raw_row in table.tbody.find_all('tr'):
        parsed_row = {row[0]: row[1] for row in _parse_row(
            raw_row, col_mapping, extractor) if row and row[0] and row[1]}
        if parsed_row:
            rows.append(parsed_row)
    return rows


def _parse_row(raw_row, col_mapping, extractor):
    for i, cell in enumerate(raw_row.find_all('td')):
        if int(cell.get('colspan', 1)) > 1:
            continue
        col_name = col_mapping[i]
        yield extractor(col_name, cell)
