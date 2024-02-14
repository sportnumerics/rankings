from collections.abc import Iterator


def years(year: str) -> Iterator[str]:
    if '-' in year:
        start, end = year.split('-')
    else:
        start = year
        end = year

    for year in range(int(start), int(end)+1):
        yield str(year)
