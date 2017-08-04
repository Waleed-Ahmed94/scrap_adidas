from sqlalchemy.orm import sessionmaker
import sqlalchemy
from models import create_products_table, Products
import settings


class ScrapAdidasPipeline(object):
    def __init__(self):

        db = settings.DATABASE['database']
        password = settings.DATABASE['password']
        user = settings.DATABASE['username']
        host = settings.DATABASE['host']
        port = settings.DATABASE['port']

        # connect with the help of the PostgreSQL URL
        # postgresql://admin:****@localhost:5432/crawl_website
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(user, password, host, port, db)
        engine = sqlalchemy.create_engine(url, client_encoding='utf8')

        # bind the connection to MetaData()
        #meta = sqlalchemy.MetaData(bind=con, reflect=True)
        create_products_table(engine)
        self.Session = sessionmaker(bind= engine)

    def process_item(self, item, spider):
        session = self.Session()
        product = Products()
        product.brand = item['brand']
        product.title = item['title']
        product.price = item['price']
        product.store_keeping_unit = item['store_keeping_unit']
        product.product_url = item['product_url']

        try:
            session.add(product)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
