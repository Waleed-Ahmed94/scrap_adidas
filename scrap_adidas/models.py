from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, Column, Integer, String, DateTime
import settings


DeclarativeBase = declarative_base()

def create_products_table(engine):
    DeclarativeBase.metadata.create_all(engine)
    
class Products(DeclarativeBase):
    __tablename__ = 'adidas_products'
    
    id = Column(Integer, primary_key = True)
    title = Column('title', String)
    brand = Column('brand', String)
    price = Column('price', String)
    store_keeping_unit = Column('store_keeping_unit', String)
    product_url = Column('product_url', String)

