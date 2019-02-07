import json
import os
import tempfile
from pathlib import Path

import pytest
from deepdiff import DeepDiff
from flask import Response
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

from depc import create_app
from depc.controllers.checks import CheckController
from depc.controllers.configs import ConfigController
from depc.controllers.grants import GrantController
from depc.controllers.rules import RuleController
from depc.controllers.sources import SourceController
from depc.controllers.teams import TeamController
from depc.controllers.users import UserController
from depc.extensions import db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_team(app):
    def _create_team(name):
        with app.app_context():
            return TeamController.create({
                'name': name
            })
    return _create_team


@pytest.fixture
def create_user(app):
    def _create_user(name):
        with app.app_context():
            return UserController.create({
                'name': name
            })
    return _create_user


@pytest.fixture
def create_grant(app):
    def _create_grant(team_id, user_id, role='member'):
        with app.app_context():
            return GrantController.create({
                'team_id': team_id,
                'user_id': user_id,
                'role': role
            })
    return _create_grant


@pytest.fixture
def create_source(app):
    def _create_source(name, team_id, plugin='Fake', conf={}):
        with app.app_context():
            return SourceController.create({
                'team_id': team_id,
                'name': name,
                'plugin': plugin,
                'configuration': conf
            })
    return _create_source


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


@pytest.fixture
def create_check(app):
    def _create_check(name, source_id, type='Threshold', parameters={}):
        with app.app_context():
            return CheckController.create({
                'source_id': source_id,
                'name': name,
                'type': type,
                'parameters': parameters
            })
    return _create_check


@pytest.fixture
def add_check(app):
    def _add_check(rule_id, checks_id):
        with app.app_context():
            return RuleController.update_checks(
                rule_id=rule_id,
                checks_id=checks_id
            )
    return _add_check


@pytest.fixture
def create_config(app):
    def _create_config(team_id, conf={}):
        with app.app_context():
            return ConfigController.create({
                'team_id': team_id,
                'data': conf
            })
    return _create_config


@pytest.fixture
def open_mock():
    def _open_mock(name):
        path = Path(__file__).resolve().parent / 'data/{}.json'.format(name)
        with path.open() as f:
            data = json.load(f)
        return data
    return _open_mock


@pytest.fixture
def is_mock_equal(open_mock):
    def _is_mock_equal(data, mock_name):
        mock = open_mock(mock_name)
        return DeepDiff(data, mock, ignore_order=True) == {}
    return _is_mock_equal
