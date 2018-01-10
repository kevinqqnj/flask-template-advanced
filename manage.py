# encoding: utf-8
#!/usr/bin/env python
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import User, Role, roles_users, Alembic
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_security.utils import encrypt_password

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, roles_users=roles_users)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import init, migrate, upgrade

    # migrate database to latest revision
    try: init()
    except: pass
    migrate()
    upgrade()

@manager.command
def dropall():
    db.drop_all()
    print("all tables dropped! remember to delete directory: migrations")

@manager.command
def clear_A():
	# heroku db upgrade failed due to Alembic version mismatch
    Alembic.clear_A()
    print("Alembic content cleared")

@manager.command
def initrole():
    db.session.add(Role(name="superuser"))
    db.session.add(Role(name="admin"))
    db.session.add(Role(name="editor"))
    db.session.add(Role(name="author"))
    db.session.add(Role(name="user"))
    pwd = os.getenv('FLASK_ADMIN_PWD') or input("Pls input Flask admin pwd:")
    db.session.add(User(email="admin", password=encrypt_password(pwd), active=True))
    db.session.commit()
    ins=roles_users.insert().values(user_id="1", role_id="1")
    db.session.execute(ins)
    db.session.commit()
    print("Roles added!")

if __name__ == '__main__':
    manager.run()
