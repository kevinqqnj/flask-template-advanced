# encoding: utf-8
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_security import Security, SQLAlchemyUserDatastore, current_user, AnonymousUser, \
    UserMixin, RoleMixin, login_required, auth_token_required, http_auth_required
from flask_security.utils import logout_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db, admin
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin._backwards import ObsoleteAttr
from ..models import User, Role, roles_users
from flask_admin import helpers as admin_helpers

# admin dashboard customized homepage
class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

# Create customized model view class
class MyModelViewBase(ModelView):
  # column formatter
  # `view` is current administrative view
  # `context` is instance of jinja2.runtime.Context
  # `model` is model instance
  # `name` is property name
  column_display_pk = True # optional, but I like to see the IDs in the list
  # column_list = ('id', 'name', 'parent')
  column_auto_select_related = ObsoleteAttr('column_auto_select_related',
                                            'auto_select_related',
                                            True)
  column_display_all_relations = True

  def is_accessible(self):
      if not current_user.is_active or not current_user.is_authenticated:
          return False
      if current_user.has_role('superuser'):
          return True
      return False

  def _handle_view(self, name, **kwargs):
      """
      Override builtin _handle_view in order to redirect users when a view is not accessible.
      """
      if not self.is_accessible():
          if current_user.is_authenticated:
              # permission denied
              abort(403)
          else:
              # login
              return redirect(url_for('security.login', next=request.url))

class MyModelViewUser(MyModelViewBase):
  column_formatters = dict(
    password=lambda v, c, m, p: '**'+m.password[-6:],
    )
  column_searchable_list = (User.email, )

# Role/User Tab: login required
admin.add_view(MyModelViewBase(Role, db.session))
admin.add_view(MyModelViewUser(User, db.session))

@main.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@main.route('/__webpack_hmr')
def npm():
    return redirect('http://localhost:8080/__webpack_hmr')

@main.route('/protected')
@login_required
def protected():
  if current_user != AnonymousUser and not current_user.is_active:
    logout_user()
    return "you've been logged out!"
  return "Success, it's protected view!"
