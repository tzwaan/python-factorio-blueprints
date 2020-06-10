from py_factorio_blueprints import util
from py_factorio_blueprints.entity import Entity as BaseEntity
from py_factorio_blueprints.exceptions import *
from py_factorio_blueprints.util import (
    Color, Tile, Connection, Vector, obj_set, Direction
)
from py_factorio_blueprints.entity_mixins import SignalName
import json


class Schedule:
    def __init__(self, blueprint, *, schedule, locomotives):
        self.blueprint = blueprint
        self.locomotives = self.find_locomotives(locomotives)
        self.schedule = schedule

    def find_locomotives(self, locomotives):
        locos = [
            self.blueprint.entities.get_by_id(loco_id)
            for loco_id in locomotives]
        return [loco for loco in locos if loco is not None]

    def to_json(self):
        return {
            'locomotives': [
                loco._auto_entity_number
                for loco in self.locomotives],
            'schedule': self.schedule
        }


class BlueprintLayer:
    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner

    def __init__(self, blueprint, obj_type, strict=True):
        self.__blueprint = blueprint
        self.strict = strict
        self.obj_type = obj_type
        self.objs = []

    def __iter__(self):
        yield from self.objs

    def __getitem__(self, vector):
        if type(vector) is tuple:
            vector = Vector(vector)

        return [obj for obj in self.objs
                if obj.top_left < vector < obj.bottom_right]

    def __delitem__(self, obj):
        if isinstance(obj, self.obj_type):
            self.objs.remove(obj)
            obj._blueprint_layer = None
        else:
            objs = self[obj]
            for obj in objs:
                self.objs.remove(obj)
                obj._blueprint_layer = None

    def add(self, obj):
        if not isinstance(obj, self.obj_type):
            raise TypeError(
                "{obj} is not of type {self.obj_type}")
        if obj._blueprint_layer is not None:
            raise DuplicateEntity(
                "Can't add Entity instance to more than one BlueprintLayer")
        if obj in self.objs:
            return
        self.objs.append(obj)
        obj._blueprint_layer = self
        self.sort()

    def make(self, *args, **kwargs):
        obj = self.obj_type(*args, **kwargs)
        self.add(obj)
        return obj

    def sort(self):
        self.__sort()
        self.__reindex()

    def _load(self, *args, **kwargs):
        obj = self.obj_type(*args, **kwargs)
        obj._blueprint_layer = self
        self.objs.append(obj)

    @property
    def blueprint(self):
        return self.__blueprint

    def rotate(self, amount, **kwargs):
        for obj in self.objs:
            obj.rotate(amount, **kwargs)
        self.sort()

    def to_json(self):
        obj = [
            obj.to_json()
            for obj in self
        ]
        if not obj:
            return None
        return obj

    def get_by_id(self, obj_id):
        if not hasattr(self.obj_type, 'ID'):
            return None
        for obj in self.objs:
            if getattr(obj, self.obj_type.ID) == obj_id:
                return obj
        return None

    def __get__(self, instance, owner):
        return self

    def __sort(self):
        self.objs.sort(key=lambda obj: (obj.position.y, obj.position.x))

    def __reindex(self):
        for i, obj in enumerate(self.objs):
            obj._auto_entity_number = i


class Blueprint:
    entity_prototypes = {}
    recipe_prototypes = {}
    item_prototypes = {}
    signal_prototypes = {}
    tile_prototypes = {}

    @classmethod
    def set_entity_prototype_data(cls, data, append=False):
        if append:
            data = {**cls.entity_prototypes, **data}
        cls.entity_prototypes = data

    @classmethod
    def set_recipe_prototype_data(cls, data, append=False):
        if append:
            data = {**cls.recipe_prototypes, **data}
        cls.recipe_prototypes = data

    @classmethod
    def set_item_prototype_data(cls, data, append=False):
        if append:
            data = {**cls.item_prototypes, **data}
        cls.item_prototypes = data

    @classmethod
    def set_signal_prototype_data(cls, data, append=False):
        if append:
            data = {**cls.signal_prototypes, **data}
        cls.signal_prototypes = data

    @classmethod
    def set_tile_prototype_data(cls, data, append=False):
        if append:
            data = {**cls.tile_prototypes, **data}
        cls.tile_prototypes = data

    @classmethod
    def import_prototype_data(cls, filename, **kwargs):
        with open(filename) as f:
            data = json.load(f)
            cls.set_entity_prototype_data(data['entity'], **kwargs)
            cls.set_recipe_prototype_data(data['recipe'], **kwargs)
            cls.set_item_prototype_data(data['item'], **kwargs)
            cls.set_signal_prototype_data(data['signal'], **kwargs)
            cls.set_tile_prototype_data(data['tile'], **kwargs)

    def __init__(self, string=None, data=None,
                 *, print2d=False,
                 entity_mixins=None, strict=True, **kwargs):
        super().__init__(**kwargs)
        self.strict = strict
        self.__entities = BlueprintLayer(self, BaseEntity, strict=strict)
        self.__tiles = BlueprintLayer(self, Tile, strict=strict)
        self.item = 'blueprint'
        self.label = ''
        self.label_color = None
        self.icons = []
        self.version = 0
        self.connections = []
        self.schedules = []

        self.__entity_mixins = entity_mixins or []

        print(string)
        if string is not None:
            data = util.decode(string)
            print(data)
        if data is not None:
            self.load(data)

        if print2d:
            self.print_2d()

    @property
    def entities(self):
        return self.__entities

    @property
    def tiles(self):
        return self.__tiles

    def load(self, data):
        if 'blueprint' in data:
            data = data['blueprint']
        # print(data)

        self.item = data.get('item', 'blueprint')
        self.label = data.get('label', None)
        label_color = data.get('label_color', None)
        if label_color is not None:
            self.label_color = Color(**label_color)
        self.version = data.get('version', 0)

        self.icons = [None, None, None, None]

        class Icon:
            name = SignalName()

        for icon in data.get('icons', []):
            # print('icon:', icon)
            new_icon = Icon()
            new_icon.name = icon['signal']
            self.icons[icon['index'] - 1] = new_icon
        # print(self.icons)

        for entity in data.get('entities', []):
            print(entity)
            self.entities._load(**entity)

        self.parse_connections()

        for tile in data.get('tiles', []):
            self.tiles._load(**tile)

        self.schedules = [
            Schedule(self, **schedule)
            for schedule in data.pop('schedules', [])
        ]

    def set_label(self, label, color=None):
        self.label = label
        if isinstance(color, Color):
            self.label_color = color
        elif color is not None:
            self.label_color = Color(**color)

    def rotate(self, amount, **kwargs):
        self.entities.rotate(amount, **kwargs)
        self.tiles.rotate(amount, **kwargs)

    def to_json(self):
        obj = {
            'item': self.item,
        }
        obj_set(obj, 'label', self.label)
        obj_set(obj, 'label_color', self.label_color)
        obj_set(obj, 'entities', self.entities.to_json())
        obj_set(obj, 'tiles', self.tiles.to_json())
        obj['icons'] = [
            {'index': i + 1, 'signal': icon.name.to_json()}
            for i, icon in enumerate(self.icons)
            if icon is not None]
        obj['version'] = self.version
        schedules = [
            schedule.to_json()
            for schedule in self.schedules]
        if schedules:
            obj['schedules'] = schedules

        return {'blueprint': obj}

    def to_json_string(self):
        return json.dumps(self.to_json())

    def to_string(self):
        obj = self.to_json()
        return util.encode(obj)

    def get_entity_by_id(self, entity_number):
        for entity in self.entities:
            if entity.entity_number == entity_number:
                return entity

    @property
    def maximum_values(self):
        maxx, minx, maxy, miny = 0, 0, 0, 0
        for entity in self.entities:
            metadata = entity.name.metadata
            height = metadata.get('height', 1)
            width = metadata.get('width', 1)
            if entity.direction.is_left or entity.direction.is_right:
                height, width = width, height
            offset = Vector((width - 1) / 2.0, -(height - 1) / 2.0)
            if entity.position.x + offset.x > maxx:
                maxx = int(entity.position.x + offset.x)
            elif entity.position.x - offset.x < minx:
                minx = int(entity.position.x - offset.x)
            if entity.position.y + offset.y > maxy:
                maxy = int(entity.position.y + offset.y)
            elif entity.position.y - offset.y < miny:
                miny = int(entity.position.y - offset.y)
        return maxx, minx, maxy, miny

    @property
    def center(self):
        maxx, minx, maxy, miny = self.maximum_values
        return Vector((maxx + minx) / 2, (maxy + miny) / 2)

    @property
    def weighted_center(self):
        center = Vector(0, 0)
        for entity in self.entities:
            center += entity.position
        center /= len(self.entities)
        return center

    @property
    def top_left(self):
        maxx, minx, maxy, miny = self.maximum_values
        return Vector(minx, miny)

    @property
    def top_right(self):
        maxx, minx, maxy, miny = self.maximum_values
        return Vector(maxx, miny)

    @property
    def bottom_left(self):
        maxx, minx, maxy, miny = self.maximum_values
        return Vector(minx, maxy)

    @property
    def bottom_right(self):
        maxx, minx, maxy, miny = self.maximum_values
        return Vector(maxx, maxy)

    @property
    def corners(self):
        maxx, minx, maxy, miny = self.maximum_values
        return (
            Vector(minx, miny), Vector(maxx, miny),
            Vector(minx, maxy), Vector(maxx, maxy))

    def recenter(self, around=None):
        if around is not None:
            center = around
        else:
            center = self.center.ceil()
        if center == Vector(0, 0):
            return
        for entity in self.entities:
            entity.position -= center
        self.replace_entities()

    def parse_connections(self):
        self.connections = []
        for entity in self.entities:
            if entity.raw_connections is not None:
                for side, connection_point in \
                        entity.raw_connections.items():
                    for color, connections in connection_point.items():
                        for connection in connections:
                            other = self.get_entity_by_id(
                                connection['entity_id'])
                            conn = Connection(
                                entity,
                                other,
                                side,
                                connection.get('circuit_id', '1'),
                                color=color)
                            if conn not in self.connections:
                                self.connections.append(conn)
        # print(len(self.connections))
        for entity in self.entities:
            connections = entity.get_connections()

    def print_2d(self, textures=None):
        """
        Print a 2d representation of the blueprint using unicode
        characters as specified.

        :Param textures: A dictionary containg specific characters for
                         specific entities. Check examples for more info.
        """
        if textures is None:
            textures = self._textures
        top_left, top_right, bottom_left, bottom_right = self.corners
        result = "\n"
        for y in range(top_left.y, bottom_left.y + 1):
            for x in range(top_left.x, top_right.x + 1):
                position = Vector(x, y)
                entity = self[position]
                if entity is None:
                    result += textures['empty']
                elif entity.name in textures:
                    texture = textures[entity.name]
                    tx, ty = entity.getTextureIndex(position)
                    result += texture[entity.direction][int(ty)][int(tx)]
                else:
                    result += textures['unknown']
            result += "\n"

        print(result)
