import unittest

from py_factorio_blueprints.blueprint import (
    Blueprint
)
from py_factorio_blueprints.entity import Entity
from py_factorio_blueprints.util import UnknownEntity


class TestBlueprint(unittest.TestCase):
    def test_data_import(self):
        blueprint1 = Blueprint()
        with self.assertRaises(UnknownEntity):
            Entity(name='transport-belt', position=(0, 0))
        Blueprint.import_prototype_data('../entity_data.json')
        Entity(name='transport-belt', position=(0, 0))
    pass


if __name__ == '__main__':
    unittest.main()
