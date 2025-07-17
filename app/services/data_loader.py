import logging
from datetime import datetime
from time import sleep
from threading import Thread

from dateutil.parser import parse
import requests

from app import db
from app.models import Product, Category
from config import Config


class DataLoaderService:
    def __init__(self, app):
        self.app = app
        self.sync_interval = Config.UPDATE_INTERVAL * 60

    def start_sync_loop(self):
        thread = Thread(target=self._sync_loop)
        thread.daemon = True
        thread.start()

    def _sync_loop(self):
        while True:
            with self.app.app_context():
                try:
                    self.sync_data()
                except Exception as e:
                    logging.error(f"Ошибка синхронизации: {str(e)}")
            sleep(self.sync_interval)

    def sync_data(self):
        logging.info("Начало синхронизации данных")

        try:
            main_data = self._fetch_data(True)
            other_data = self._fetch_data(False)

            if main_data and 'categories' in main_data:
                self._process_categories(main_data['categories'])

            if other_data and 'products' in other_data:
                self._process_products(other_data['products'])

            logging.info("Синхронизация данных успешно завершена")
            return True

        except Exception as e:
            logging.error(f"Ошибка при синхронизации данных: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def _fetch_data(on_main):
        url = f"{Config.API_BASE_URL}?on_main={'true' if on_main else 'false'}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при запросе к API (on_main={on_main}): {str(e)}")
            return None

    @staticmethod
    def _process_categories(categories_data):
        if not categories_data:
            return

        for category_data in categories_data:
            if not category_data.get('Category_ID') or not category_data.get('Category_Name'):
                continue

            category = Category.query.filter_by(id=category_data['Category_ID']).first()
            if not category:
                category = Category(
                    id=category_data['Category_ID'],
                    name=category_data['Category_Name'],
                    sort_order=category_data.get('sort_order', 0)
                )
                db.session.add(category)

        db.session.commit()

    def _process_products(self, products_data):
        if not products_data:
            return

        for product_data in products_data:
            try:
                self._process_single_product(product_data)
            except Exception as e:
                logging.error(f"Ошибка обработки товара {product_data.get('Product_ID')}: {str(e)}")
                db.session.rollback()

        db.session.commit()

    def _process_single_product(self, product_data):
        if not product_data.get('Product_ID'):
            logging.warning("Пропуск товара - отсутствует ID")
            return

        if not product_data.get('parameters') or not product_data['parameters'][0].get('price'):
            logging.warning(f"Пропуск товара {product_data['Product_ID']} - отсутствует цена")
            return

        category = self._get_product_category(product_data)
        if not category:
            logging.warning(f"Пропуск товара {product_data['Product_ID']} - не найдена категория")
            return

        main_image = self._get_main_image(product_data.get('images', []))

        product = Product.query.filter_by(id=product_data['Product_ID']).first()
        price = product_data['parameters'][0]['price']

        if not product:
            product = Product(
                id=product_data['Product_ID'],
                name=product_data['Product_Name'],
                image=main_image,
                created_at=parse(product_data['Created_At']) if product_data.get('Created_At') else datetime.utcnow(),
                updated_at=parse(product_data['Updated_At']) if product_data.get('Updated_At') else datetime.utcnow(),
                price=float(price),
                on_main=False,  # Все товары из on_main=false
                category_id=category.id
            )
            db.session.add(product)
        else:
            product.name = product_data['Product_Name']
            product.image = main_image
            product.price = float(price)
            product.category_id = category.id

    @staticmethod
    def _get_product_category(product_data):
        if not product_data.get('categories') or not product_data['categories'][0].get('Category_Name'):
            return None

        category_name = product_data['categories'][0]['Category_Name']
        category = Category.query.filter_by(name=category_name).first()

        if not category:
            category = Category(
                name=category_name,
                sort_order=product_data['categories'][0].get('sort_order', 0)
            )
            db.session.add(category)
            db.session.flush()

        return category

    @staticmethod
    def _get_main_image(images_data):
        if not images_data:
            return None

        for img in images_data:
            if img.get('MainImage') and img.get('Image_URL'):
                return img['Image_URL']

        return images_data[0]['Image_URL'] if images_data and images_data[0].get('Image_URL') else None
