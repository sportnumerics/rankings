def parse_table(table, extractor, cls=dict, header_row=None):
    col_mapping = {}
    if header_row is None:
        header_row = table
    for i, heading in enumerate(header_row.find_all('th')):
        col_mapping[i] = ''.join(heading.stripped_strings)
    rows = []
    for raw_row in table.find_all('tr'):
        try:
            cols = [
                col for col in _parse_row(raw_row, col_mapping, extractor)
                if col is not None
            ]
            if cols:
                parsed_row = cls(**{
                    k: v
                    for col in cols
                    for k, v in col.items()
                })
                if parsed_row:
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
