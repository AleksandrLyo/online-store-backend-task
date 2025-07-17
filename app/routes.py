import logging

from flask import Blueprint

from app.models import Product, Category
from app import db

bp = Blueprint('main', __name__)


@bp.route('/info', methods=['GET'])
def get_info():
    try:
        total_products = Product.query.count()

        categories = db.session.query(
            Category.name,
            db.func.count(Product.id)
        ).join(Product).group_by(Category.name).order_by(Category.name).all()

        categories_str = ", ".join([f"{cat[0]} ({cat[1]})" for cat in categories])

        expensive_products = Product.query.order_by(
            Product.price.desc()
        ).limit(3).all()

        response = [
            f"Всего товаров: {total_products}",
            f"Категории: {categories_str}",
            "",
            "Самые дорогие товары:"
        ]

        for i, product in enumerate(expensive_products, 1):
            image_info = f"\n{product.image}" if product.image else ""
            response.append(
                f"{i}. {product.name.lower()} - {product.price} руб.{image_info}"
            )

        return "\n".join(response), 200

    except Exception as e:
        logging.error(f"Error generating info: {str(e)}")
        return "Internal Server Error", 500
