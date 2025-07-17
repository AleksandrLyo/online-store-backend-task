from datetime import datetime

from sqlalchemy import ForeignKey

from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    products = db.relationship('Product', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price = db.Column(db.Float, nullable=False)
    on_main = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, ForeignKey('categories.id'), nullable=False)

    category = db.relationship('Category', back_populates='products')

    def __repr__(self):
        return f'<Product {self.name}>'
