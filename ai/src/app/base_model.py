from typing import Any, List, TypeVar, Callable, Type, cast

from peewee import Model, PostgresqlDatabase

def get_db():
    return PostgresqlDatabase(
        "video_script_research",
        user="root",
        password="password",
        host="database",
        port=5432,
    )


class BaseDBModel(Model):
    class Meta:
        database = get_db()


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()
