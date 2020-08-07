import unittest
import json

from deepdiff import DeepDiff

from py_factorio_blueprints.util import UnknownEntity, Vector, decode
from py_factorio_blueprints.exceptions import *
from tests.util import _import


class TestBlueprint(unittest.TestCase):
    def test_empty_prototype_data(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        blueprint = Blueprint()
        with self.assertRaises(UnknownEntity):
            blueprint.entities.make(
                name='transport-belt', position=(0, 0))

    def test_prototype_data_import(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        blueprint = Blueprint()
        with self.assertRaises(UnknownEntity):
            blueprint.entities.make(
                name='transport-belt', position=(0, 0))
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        entity = blueprint.entities.make(
            name='transport-belt', position=(0, 0))
        self.assertIn(entity, blueprint.entities)

    def test_add_entity(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Entity = _import(
            'py_factorio_blueprints.entity', 'Entity')
        blueprint = Blueprint()
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        self.assertIsInstance(blueprint, Blueprint)
        entity = Entity(name='transport-belt', position=(0, 0))
        self.assertIsInstance(entity, Entity)
        blueprint.entities.add(entity)
        self.assertIn(entity, blueprint.entities)

    def test_make_entity(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Entity = _import(
            'py_factorio_blueprints.entity', 'Entity')
        blueprint = Blueprint()
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        entity = blueprint.entities.make(name='transport-belt', position=(0, 0))
        self.assertIsInstance(entity, Entity)
        self.assertIn(entity, blueprint.entities)

    def test_del_entity(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        blueprint = Blueprint()
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        entity = blueprint.entities.make(name='transport-belt', position=(0, 0))
        self.assertIn(entity, blueprint.entities)
        del blueprint.entities[entity]
        self.assertNotIn(entity, blueprint.entities)

    def test_getitem(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        blueprint = Blueprint()
        entities = []
        for x in range(5):
            for y in range(5):
                entities.append(
                    blueprint.entities.make(
                        name='transport-belt', position=(x, y)))

        i = 0
        for x in range(5):
            for y in range(5):
                for j, entity in enumerate(entities):
                    if i == j:
                        self.assertIn(entity, blueprint.entities[(x, y)])
                    else:
                        self.assertNotIn(entity, blueprint.entities[(x, y)])
                i += 1

    def test_misc(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Entity = _import(
            'py_factorio_blueprints.entity', 'Entity')
        blueprint1 = Blueprint()
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        entity1 = blueprint1.entities.make(name='transport-belt', position=(1, 2))
        entity2 = Entity(name='transport-belt', position=(1, 0))
        entity3 = Entity(name='transport-belt', position=(0, 1))
        entity4 = Entity(name='transport-belt', position=(1, 1))
        entity5 = Entity(name='transport-belt', position=(1, 0))

        with self.assertRaises(DuplicateEntity):
            blueprint1.entities.add(entity1)
        blueprint1.entities.add(entity2)
        blueprint1.entities.add(entity3)
        blueprint1.entities.add(entity4)
        blueprint1.entities.add(entity5)

        entities = blueprint1.entities[(1, 0)]
        self.assertNotIn(entity1, entities)
        self.assertIn(entity2, entities)
        self.assertNotIn(entity3, entities)
        self.assertNotIn(entity4, entities)
        self.assertIn(entity5, entities)

        self.assertIn(entity2, blueprint1.entities)
        del blueprint1.entities[entity2]
        self.assertNotIn(entity2, blueprint1.entities)
        pass


class TestBlueprintStringImport(unittest.TestCase):
    def test_import_balancer(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        with open('blueprint_strings/4x4_balancer_yellow_belt.blueprint') as f:
            string = f.read()
            blueprint = Blueprint(string=string)

    def test_import_connections(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        with open('blueprint_strings/combinators.blueprint') as f:
            string = f.read()
            blueprint = Blueprint(string=string)

        entity = blueprint.entities[(-1.5, -1)][0]
        self.assertEqual(entity.name, 'decider-combinator')

    def test_rail(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        string = '0eNqV0e8KgjAUBfB3OZ9n+JdirxIRapca6J24WYns3ZsKEWVYHzc4v3O3O6CoOmpaxRZygCo1G8j9AKPOnFfjne0bgoSyVEOA83o8tbmq4AQUn+gOGTmxGrlpfSIOygsZ+xKN3UGA2CqraK6eDv2Ru7qg1ttPwVhfe77YYGoXaLTxKc1jpZeCWKCHDN04zBsSL4/xaYSbbFY22ZKT/OisMOmfTPDFyf591gz5H592I1+2L3Cl1kyR7TaJoizcpbvIuQfSu7JK'
        blueprint = Blueprint(string=string)
        print(blueprint.to_json_string())
        print(blueprint.to_string())
        blueprint.rotate(1)
        print(blueprint.to_json_string())
        print(blueprint.to_string())

    def test_tiles(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        with open('blueprint_strings/tiles.blueprint') as f:
            string = f.read()

        with open('blueprint_strings/tiles_rotated.blueprint') as f:
            string_rotated = f.read()

        blueprint = Blueprint(string=string)
        blueprint_rotated = Blueprint(string=string_rotated)
        blueprint.rotate(1)
        print(blueprint.to_json_string())
        print(blueprint.to_string())
        print(blueprint_rotated.to_json_string())
        print(blueprint_rotated.to_string())
        self.assertEqual(blueprint, blueprint_rotated)

    def test_vanilla_entity_imports(self):
        Blueprint = _import(
            'py_factorio_blueprints.blueprint', 'Blueprint',
            clear=True)
        Blueprint.import_prototype_data('../py_factorio_blueprints/entity_data.json')
        print(f"Number of entities: {len(Blueprint.entity_prototypes)}")

        with open('blueprint_strings/combinators.blueprint') as f:
            string = f.read()
        print("original string:")
        print(string)
        blueprint = Blueprint(string=string)
        json_obj = blueprint.to_json()

        data = decode(string)
        print(json.dumps(data))
        print(json.dumps(json_obj))

        ddiff = DeepDiff(data, json_obj, ignore_order=True)
        print(ddiff)

        with open('blueprint_strings/entities_test.blueprint') as f:
            string = f.read()

        with open('blueprint_strings/entities_test_rotated.blueprint') as f:
            string_rotated = f.read()

        blueprint = Blueprint(string=string)
        blueprint_rotated = Blueprint(string=string_rotated)

        print(blueprint.to_string())
        print(blueprint_rotated.to_string())

        blueprint.rotate(1)

        print(blueprint.to_string())

        self.assertEqual(blueprint, blueprint_rotated)

        # ddiff = DeepDiff(json1, json2, ignore_order=True)
        # print(json.dumps(ddiff))

        # json_obj = blueprint.to_json()
        # data = decode(string)
        # print(json.dumps(data))
        # print(json.dumps(json_obj))

        # ddiff = DeepDiff(data, json_obj, ignore_order=True)
        # print(ddiff)

        # blueprint.rotate(1)
        # json_obj = blueprint.to_json()
        # data = decode(string)
        # print(json.dumps(data))
        # print(json.dumps(json_obj))
        # print(blueprint.to_string())


if __name__ == '__main__':
    unittest.main()
