#database.py
from fastapi import HTTPException
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Base, Products, Users_Contact, Users, ArchivedProducts, PriceHistory
import os


load_dotenv()
#здесь мы создаем пулл соединений, он нужен чтобы не ебать мозг базе данных каждый раз когда создается транзакция,
# максимум я поставил 10, но если их не хватит, бд автоматически башляет еще 10
engine = create_engine(
    url=os.getenv('DB_URL'),
    echo=False,
    pool_size=10,
    max_overflow=10,
    pool_timeout=10
)

#db utils func - всякие вспомогательные функции
def check_product_id(product_id: int):
    try:
        with Session(engine) as se:
            # noinspection PyTypeChecker
            fresh_price = se.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                (func.now() - PriceHistory.created_at) <= timedelta(hours=1)
            ).first()
            return False if fresh_price else True
    except Exception as e:
        print(f"error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
def set_secondary_all(user_id: int):
    try:
        with Session(engine) as se:
            contacts = se.query(Users_Contact).filter(and_(
                Users_Contact.user_id == user_id,
            )).all()
            print(contacts)
            for contact in contacts:
                contact.is_primary = "secondary"
            se.commit()
    except HTTPException:
        raise

def registration(username: str):
    try:
        with Session(engine) as se:
            new_user = Users(username = username)
            se.add(new_user)
            se.commit()
            se.refresh(new_user)
            user_id = search_user_by_username(username)
            return user_id
    except Exception as e:
        print(f"error as {e}")
        raise HTTPException(status_code=500, detail="Internal server Error")
def save_new_contact(platform: str, contact_value: str, user_id: int, is_primary: str):
    try:
        with Session(engine) as se:
            new_contact = Users_Contact(platform=platform, contact_value=contact_value, user_id=user_id, is_primary = is_primary)
            se.add(new_contact)
            se.commit()
            se.refresh(new_contact)
    except Exception as e:
        print(f"ERROR as {e}")
        raise HTTPException(status_code=500, detail="Internal server Error")
    else:
        return contact_value

def authorization(username: str, user_id:int): #<--типо авторизация
    with Session(engine) as se:
        username_exp = se.query(Users).filter_by(user_id = user_id).first()
        return username_exp.username == username

def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
#проверка на уникальность никнейма, по идее можно было бы объединить с функцией поиска по контакту, но западло мешать мочу с матчей
def search_user_by_username(username: str):
    try:
        with Session(engine) as se:
            res = se.query(Users).filter_by(
                username = username
            ).first()
            if res:
                user_id = res.user_id
                return user_id
            return None
    except Exception as e:
        raise f"error {e}"

# функция поиска по контакту, контакт - термин означающий вкупе платформу и идентификатор пользователя
def search_user_by_contact(contact_value: str, platform: str):
    try:
        with Session(engine) as se:
            res = se.query(Users_Contact).filter_by(
                contact_value = contact_value,
                platform = platform
            ).first()
            if res:
                user_id = res.user_id
                return user_id
            else:
                return None
    except Exception as e:
        raise Exception(f"error {e}")
#это короче чтоб бд не дрочила десять тысяч типов разных айдишников, а только внутренний для бд user_id, если понадобится сохранить id платформы,
# а не моего сервиса, то уж будь добр делать это в эндпоинте
def normalize_id(platform: str, contact_value: str):
    try:
        with Session(engine) as se:
            res = se.query(Users_Contact).filter_by(
                contact_value = contact_value,
                platform = platform
            ).first()
            if res:
                return res.user_id
            else:
                raise HTTPException(status_code=404, detail="No user found")
    except Exception as e:
        print(f"Database error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
#тут и так понятно, по идее матрешка, но код выглядит чище для меня
def is_user_exist(contact_value: str, platform: str):
    return search_user_by_contact(contact_value, platform)

#db endpoint func - функции в которых конкретно работают с бд, нужно для эндпоинтов
def insert_data(product, platform: str, contact_value: str):
    try:
        with Session(engine) as se:
            user_id = is_user_exist(contact_value, platform)
            if user_id:
                new_product = Products(
                    name = product.name,
                    amount = product.amount,
                    price = product.price,
                    description = product.description,
                    user_id = user_id)
                se.add(new_product)
                se.commit()
                se.refresh(new_product)
            else:
                raise HTTPException(status_code=404, detail="No user found, go register suka")
    except IntegrityError:
        raise HTTPException(status_code=409, detail='Product already exist')
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error {e}")
        raise HTTPException(status_code=500, detail='Internal server error')
    else:
        return {"id": new_product.product_id, "name": new_product.name}

def get_all(contact_value: str, platform: str):
    try:
        with Session(engine) as se:
            if user_id := search_user_by_contact(contact_value, platform):
                data = se.query(Products).filter_by(user_id = user_id).all()
                if not data:
                    raise HTTPException(status_code=404, detail="No products found")
                return data
            raise HTTPException(status_code=404, detail="No user found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def post_get_in(platform: str, contact_value:str, username:str, is_primary: bool):
    try:
        if user_id := search_user_by_contact(contact_value, platform): #та же платформа, авторизация
            user_flag = authorization(username, user_id)
            print("auth")
            if user_flag:
                return {"user_id": user_id,
                        "username": username,
                        "platform": platform,
                        "contact_value": contact_value,
                        "is_primary": is_primary,
                        "jwt_token": "hui tebe a ne token ahahahah"}
            raise HTTPException(401, "Invalid username or password")
        elif not user_id: #не та же платформа, авторизация
            if user_id := search_user_by_username(username):
                user_flag = authorization(username, user_id)
                if user_flag:
                    if is_primary:
                        set_secondary_all(user_id)
                        contact_value = save_new_contact(platform, contact_value, user_id, "primary")
                    else:
                        contact_value = save_new_contact(platform, contact_value, user_id, "secondary")
                    print("auth_new")
                    return {"user_id": user_id,
                            "username": username,
                            "platform": platform,
                            "contact_value": contact_value,
                            "is_primary": is_primary,
                            "jwt_token": "hui tebe a ne token ahahahah"}
                raise HTTPException(401, "Invalid username or password")
            elif not user_id: #регистрация
                print("reg")
                user_id = registration(username)
                set_secondary_all(user_id)
                save_new_contact(platform, contact_value, user_id, is_primary = "primary" if is_primary else "secondary")
                return {"user_id": user_id,
                        "username": username,
                        "platform": platform,
                        "contact_value": contact_value,
                        "is_primary": is_primary,
                        "jwt_token": "hui tebe a ne token ahahahah"}
    except HTTPException:
        raise

def archive(platform: str, contact_value: str, product_id: int):
    try:
        with Session(engine) as se:
            user_id = search_user_by_contact(contact_value, platform)
            if not user_id:
                raise HTTPException(404, "User not found")
            product = se.query(Products).filter_by(product_id=product_id).first()
            if not product:
                raise HTTPException(404, "Product not found")
            if user_id != product.user_id:
                raise HTTPException(403, "You are not the owner of this product")
            archived_product = ArchivedProducts(
                name=product.name,
                amount=product.amount,
                price=product.price,
                description=product.description,
                user_id=product.user_id)
            se.add(archived_product)
            se.delete(product)
            se.commit()
            return {"message": "Product archived"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(500, "Internal server error")

def save_price_history(product_id: int, value: float):
    try:
        product_id_flag = check_product_id(product_id)
        with Session(engine) as se:
            if product_id_flag:
                new_price_value = PriceHistory(product_id = product_id, value = value)
                se.add(new_price_value)
                se.commit()
                se.refresh(new_price_value)
            else:
                raise HTTPException(status_code= 418, detail="I`m a teapot")
            return {"product_id": product_id,
                    "value": value,
                    "created_at":new_price_value.created_at}
    except IntegrityError:
        raise HTTPException(status_code=409, detail='Product not found')
    except HTTPException as e:
        print(f"error {e}")
        raise
