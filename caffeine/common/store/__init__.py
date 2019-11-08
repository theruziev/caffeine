from pydantic.main import BaseModel
from pydantic.types import PositiveInt


class SortInt(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v not in [1, 0, -1]:
            raise ValueError(f"-1 for ASC 0 no sort and 1 for DESC expected not {v}")
        return v


class Paginator(BaseModel):
    per_page: PositiveInt = 20
    page: PositiveInt = 1
