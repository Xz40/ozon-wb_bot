#models
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func

Base = declarative_base()

class Products(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("Users", back_populates="products")

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    products = relationship("Products", back_populates="user")
    contacts = relationship("Users_Contact", back_populates="user")

class Users_Contact(Base):
    __tablename__ = "users_contact"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    platform = Column(String(100), nullable=False)
    contact_value = Column(String(100), nullable=False)
    is_primary = Column(String(100), default="primary")
    user = relationship("Users", back_populates="contacts")

class ArchivedProducts(Base):
    __tablename__ = "archived_products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    archived_at = Column(DateTime, default = func.now())

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'))
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())