# encoding: utf-8
from flask import Flask, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_security import Security, SQLAlchemyUserDatastore, current_user, \
    UserMixin, RoleMixin, login_required, auth_token_required, http_auth_required
from flask_security.utils import encrypt_password
from flask_admin.contrib import sqla
from flask_admin import Admin, helpers as admin_helpers

db = SQLAlchemy()

# models must be imported after db/login_manager
from .models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

# Create admin
admin = Admin(name=u'Admin Board')

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	db.init_app(app)
	# datastore must be set after app created
	security.init_app(app, datastore=user_datastore)
	admin.init_app(app)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	return app
