import dataclasses
import os
import pathlib
from types import UnionType
from typing import IO, Optional, TypeVar
from collections.abc import Iterator, Iterable
import itertools
import json
import typing

import pyarrow
import pyarrow.parquet as pq

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
    return (cls.from_dict(d) for d in data)


def load_from_files(cls: type[T], filenames: Iterable[str]) -> Iterable[T]:
    for file in filenames:
        with open(file) as f:
            yield load(cls, f)


R = TypeVar('R')


def dump_parquet(data: Iterable[R], filename: str):
    dir = os.path.dirname(filename)
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    it = iter(data)
    first = next(it)
    schema = get_schema(first)
    table = pyarrow.Table.from_pylist(
        [dataclasses.asdict(d) for d in itertools.chain([first], it)],
        schema=schema)
    pq.write_table(table, filename)


def parquet_path(out_dir: str, year: str, dataset_name: str, *rest: list[str]):
    return os.path.join(out_dir, year, 'v2', dataset_name, *rest)


def load_parquet(cls: type[R], filename: str) -> Iterable[R]:
    return (cls.from_dict(r) for r in pq.read_table(filename).to_pylist())


def load_parquet_dataset(cls: type[R], path: str) -> Iterable[R]:
    schema = get_schema(cls)
    return (cls.from_dict(r)
            for r in pq.ParquetDataset(path, schema=schema).read().to_pylist())


def get_schema(cls: type[R]) -> pyarrow.Schema:
    return pyarrow.schema([(field.name, get_pyarrow_type(field.type))
                           for field in dataclasses.fields(cls)])


def get_pyarrow_type(field: any) -> pyarrow.DataType:
    if dataclasses.is_dataclass(field):
        return pyarrow.struct([(field.name, get_pyarrow_type(field.type))
                               for field in dataclasses.fields(field)])
    origin = typing.get_origin(field)
    if origin is UnionType or origin is Optional:
        return get_pyarrow_type(
            next(f for f in typing.get_args(field) if f is not type(None)))
    if origin is list:
        return pyarrow.list_(get_pyarrow_type(typing.get_args(field)[0]))

    return pyarrow.from_numpy_dtype(field)
