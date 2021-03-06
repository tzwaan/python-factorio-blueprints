import unittest

from py_factorio_blueprints.entity import Entity
from py_factorio_blueprints.util import UnknownEntity
from tests.util import _import


class TestEntity(unittest.TestCase):
    def test_entity_name(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        with self.assertRaises(TypeError):
            Entity()
        with self.assertRaises(UnknownEntity):
            entity = Entity(name='transport-belt', position=(0, 0))
        Blueprint.set_entity_prototype_data(
            {
                'transport-belt': {
                    'type': 'transport-belt',
                    'height': 1,
                    'width': 1,
                    'selection_box': {
                        'left_top': {
                            'x': -0.5,
                            'y': -0.5,
                        },
                        'right_bottom': {
                            'x': 0.5,
                            'y': 0.5,
                        }
                    }
                },
            })
        entity = Entity(name='transport-belt', position=(0, 0))
        self.assertEqual(entity.name, 'transport-belt')
        Blueprint.set_entity_prototype_data(
            {
                'underground-belt': {
                    'type': 'underground-belt',
                    'height': 1,
                    'width': 1,
                    'selection_box': {
                        'left_top': {
                            'x': -0.5,
                            'y': -0.5,
                        },
                        'right_bottom': {
                            'x': 0.5,
                            'y': 0.5,
                        }
                    }
                }
            },
            append=True
        )
        entity = Entity(name='transport-belt', position=(0, 0))
        self.assertEqual(entity.name, 'transport-belt')
        entity = Entity(name='underground-belt', position=(0, 0), type='input')
        self.assertEqual(entity.name, 'underground-belt')
        self.assertEqual(entity.type, 'input')
