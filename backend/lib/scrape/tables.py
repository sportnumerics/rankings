def parse_table(table, extractor, cls=dict):
    col_mapping = {}
    for i, heading in enumerate(table.thead.find_all('th')):
        col_mapping[i] = ''.join(heading.stripped_strings)
    rows = []
    for raw_row in table.tbody.find_all('tr'):
        try:
            cols = [
                col for col in _parse_row(raw_row, col_mapping, extractor)
                if col and col[0] and col[1]
            ]
            if cols:
                parsed_row = cls(**{col[0]: col[1] for col in cols})
                rows.append(parsed_row)
        except Exception as e:
            raise Exception(f'Unable to parse table row {raw_row}', e)
    return rows


def _parse_row(raw_row, col_mapping, extractor):
    for i, cell in enumerate(raw_row.find_all('td')):
        if int(cell.get('colspan', 1)) > 1:
            continue
        col_name = col_mapping[i]
        yield extractor(col_name, cell)
