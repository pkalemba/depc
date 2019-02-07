import json
import os
import tempfile

import pytest
from flask import Response
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from depc.controllers.rules import RuleController


from depc import create_app
from depc.extensions import db


class DepcTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self._login = None
        super(DepcTestClient, self).__init__(*args, **kwargs)

    def login(self, login):
        self._login = login

    def logout(self):
        self._login = None

    def open(self, *args, **kwargs):
        headers = kwargs.pop('headers', Headers())

        if self._login:
            headers.extend({'X-Remote-User': self._login})
            kwargs['headers'] = headers
        return super().open(*args, **kwargs)


class DepcResponse(Response):

    def remove_keys(self, d, keys):
        if isinstance(keys, str):
            keys = [keys]
        if isinstance(d, dict):
            for key in set(keys):
                if key in d:
                    del d[key]
            for k, v in d.items():
                self.remove_keys(v, keys)
        elif isinstance(d, list):
            for i in d:
                self.remove_keys(i, keys)
        return d

    @property
    def json(self):
        data = json.loads(self.data.decode('utf-8'))
        self.remove_keys(data, ['id', 'createdAt', 'updatedAt', 'created_at', 'updated_at'])
        return data

    def raises_required_property(self, prop):
        wanted = {'message': "'{}' is a required property".format(prop)}
        return self.status_code == 400 and self.json == wanted


@pytest.fixture(scope='module')
def app_module():
    db_fd = db_path = None
    app = create_app(
        environment='test',
    )

    # Choose tests database
    if app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite://':
        db_fd, db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}.db'.format(db_path)

    with app.app_context():
        db.create_all()

    app.response_class = DepcResponse
    app.test_client_class = DepcTestClient
    yield app

    with app.app_context():
        db.drop_all()

    if db_fd and db_path:
        os.close(db_fd)
        os.unlink(db_path)

    return app_module


@pytest.fixture(scope='function')
def app(app_module):
    with app_module.app_context():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    return app_module


@pytest.fixture
def create_rule(app):
    def _create_rule(name, team_id, description=None):
        with app.app_context():
            return RuleController.create({
                'team_id': team_id,
                'name': name,
                'description': description
            })
    return _create_rule
