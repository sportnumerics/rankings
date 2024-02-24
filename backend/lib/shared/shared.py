from dataclasses import asdict
from textwrap import indent
from typing import IO
from collections.abc import Collection, Iterator, Iterable
import json
import typing

from .types import BaseType


def years(year: str) -> Iterator[str]:
    if '-' in year:
        start, end = year.split('-')
    else:
        start = year
        end = year

    for year in range(int(start), int(end) + 1):
        yield str(year)


def dump(obj: BaseType | Iterable[BaseType], fp: IO, many: bool = False):
    if many:
        data = [o.to_dict() for o in typing.cast(Iterable[BaseType], obj)]
    else:
        data = obj.to_dict()
    json.dump(data, fp, indent=2)
