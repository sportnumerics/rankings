from dataclasses import asdict
from textwrap import indent
from typing import IO, TypeVar
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


def load(cls: type[BaseType], fp: IO) -> BaseType:
    data = json.load(fp)
    return cls.from_dict(data)


T = TypeVar('T', bound=BaseType)


def load_many(cls: type[T], fp: IO) -> Iterable[T]:
    data: Iterable[dict] = json.load(fp)
    return [cls.from_dict(d) for d in data]


def load_from_files(cls: type[T], filenames: Iterable[str]) -> Iterable[T]:
    for file in filenames:
        with open(file) as f:
            yield load(cls, f)
