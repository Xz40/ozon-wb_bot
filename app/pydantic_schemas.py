#pydantic_schemas.py
from pydantic import BaseModel

class ProductIn(BaseModel):
    name: str
    amount: int
    price: float
    description: str | None = None

class ProductResponse(ProductIn):
    product_id: int

class UserProductsResponse(BaseModel):
    contact_value: str | int
    platform: str
    products: list[ProductResponse]

class User(BaseModel):
    platform: str
    contact_value: str
    username: str
    is_primary: bool | None = True

class UserResponse(BaseModel):
    user_id: int
    username: str
    platform: str
    contact_value: str
    is_primary: bool
    jwt_token: str | None = None