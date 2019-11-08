from pydantic import BaseModel, PositiveInt


class Paginator(BaseModel):
    page: PositiveInt = 1
    per_page: PositiveInt = 20
