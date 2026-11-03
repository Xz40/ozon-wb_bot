#crud.py
from database import insert_data, get_all, post_get_in, archive, save_price_history
from pydantic_schemas import ProductIn, UserResponse, UserProductsResponse
from fastapi import APIRouter
router = APIRouter()

@router.get('/health')
async def get_health():
    return {"status": "200 OK"}

@router.get('/')
async def info():
    return {"info":"Automated price scraper for marketplaces"}

#CREATE
@router.post('/new_product', status_code=201)
async def get_new_product(product: ProductIn, platform: str, contact_value: str):
    return insert_data(product, platform, contact_value)
#CREATE
@router.post('/get_in', status_code=201, response_model=UserResponse)
async def register(platform: str, contact_value: str, username: str, is_primary:bool):
    return post_get_in(platform, contact_value, username, is_primary)
@router.post('/insert_price')
async def price_history(product_id: int, value:int):
    return save_price_history(product_id, value)
#DELETE
@router.delete("/archive_product")
async def archive_endpoint(platform: str, contact_value: str, product_id: int):
    return archive(platform, contact_value, product_id)
#READ
@router.get('/user_products', status_code=200, response_model=UserProductsResponse)
async def get_all_products(contact_value: str, platform: str):
    data = get_all(contact_value, platform)
    return {
        "contact_value": contact_value,
        "platform": platform,
        "products": data
    }



