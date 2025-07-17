import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

    with app.app_context():
        from app.services.data_loader import DataLoaderService
        DataLoaderService(app).start_sync_loop()

        try:
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {str(e)}")

    return app


from app import models
