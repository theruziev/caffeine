from enum import Enum

from pydantic.main import BaseModel


class ProductTypeEnum(str, Enum):
    simple = "simple"
    variative = "variative"


class ProductStatusEnum(str, Enum):
    published = "published"
    draft = "draft"
    out_of_stock = "out_of_stock"


class ProductCategory(BaseModel):
    id: int = None
    title: str
    slug: str
    parent_id: str
    is_active: bool = False


class Product(BaseModel):
    id: int = None
    title: str
    slug: str
    sku: str
    status: ProductStatusEnum = ProductStatusEnum.draft
    stock: int
    price: int
    parent_id: int = None
    long_description: str
    description: str
    image: str
    meta_keywords: str
    meta_description: str
    type: ProductTypeEnum = ProductTypeEnum.simple


class ProductOption(BaseModel):
    id: int = None
    product_id: int
    name: str
    value: str
