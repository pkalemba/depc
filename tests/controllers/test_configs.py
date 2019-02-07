import pytest


def test_create_context_from_config():
    from depc.apiv1.configs import ConfigController
    controller = ConfigController()

    config = {'Offer': {'qos': 'aggregation.AVERAGE[Website]'}, 'Filer': {'qos': 'rule.Servers'},
              'Website': {'qos': 'operation.AND[Filer, Apache]'}, 'Apache': {'qos': 'rule.Servers'}}

    config_context = controller._create_context_from_config(config)

    assert config_context == {
        'labels_with_parent': {'Website': ('Offer', 'aggregation'), 'Filer': ('Website', 'operation'),
                               'Apache': ('Website', 'operation')},
        'all_labels': {'Website': {'dependencies': ['Filer', 'Apache'], 'compute_type': 'operation'},
                       'Filer': {'rule_name': 'Servers', 'compute_type': 'rule'},
                       'Offer': {'dependencies': ['Website'], 'compute_type': 'aggregation'},
                       'Apache': {'rule_name': 'Servers', 'compute_type': 'rule'}}}


def test_check_config_from_context(create_rule):
    from depc.apiv1.configs import ConfigController
    controller = ConfigController()

    team_id = '533cbab1-f824-4160-beab-b54f3ea52335'

    create_rule('Servers', team_id)

    config_context = {'labels_with_parent': {'Website': ('Offer', 'aggregation'), 'Filer': ('Website', 'operation'),
                                              'Apache': ('Website', 'operation')},
                       'all_labels': {'Website': {'dependencies': ['Filer', 'Apache'], 'compute_type': 'operation'},
                                      'Filer': {'rule_name': 'Servers', 'compute_type': 'rule'},
                                      'Offer': {'dependencies': ['Website'], 'compute_type': 'aggregation'},
                                      'Apache': {'rule_name': 'Servers', 'compute_type': 'rule'}}}


    controller._check_config_from_context(config_context, team_id)
