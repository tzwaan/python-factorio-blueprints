import logging
from py_factorio_blueprints import util
from py_factorio_blueprints.entity import Entity as BaseEntity
from py_factorio_blueprints.exceptions import *
from py_factorio_blueprints.util import (
    Color, Tile, Connection, Vector, obj_set, Direction
)
from py_factorio_blueprints.entity_mixins import SignalName
import json


logger = logging.getLogger('py_factorio_blueprints.blueprint')


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
                if obj.collides(vector)]

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
        if obj._blueprint_layer is not None and obj._blueprint_layer != self:
            raise DuplicateEntity(
                "Can't add Entity instance to more than one BlueprintLayer")
        if obj in self.objs:
            return
        self.objs.append(obj)
        obj._blueprint_layer = self
        self.sort()

    def make(self, *args, **kwargs):
        obj = self.obj_type(*args, blueprint_layer=self, **kwargs)
        self.add(obj)
        return obj

    def sort(self):
        self.__sort()
        self.__reindex()

    def _load(self, *args, **kwargs):
        obj = self.obj_type(*args, blueprint_layer=self, **kwargs)
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
            obj._auto_entity_number = i + 1


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
                 *, custom_entity_prototypes=None, strict=True,
                 verbose=False, **kwargs):
        super().__init__(**kwargs)
        self._verbose = verbose
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

        if custom_entity_prototypes is None:
            custom_entity_prototypes = {}
        self.custom_entity_prototypes = custom_entity_prototypes

        logger.debug(string)
        if string is not None:
            data = util.decode(string)
            logger.debug(data)
        if data is not None:
            self.load(data)

    def __eq__(self, other):
        if not isinstance(other, Blueprint):
            return NotImplemented
        return self.to_string() == other.to_string()

    @property
    def entities(self):
        return self.__entities

    @property
    def tiles(self):
        return self.__tiles

    def load(self, data):
        if 'blueprint' in data:
            data = data['blueprint']
        logger.debug(data)

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
            logger.debug('icon:', icon)
            new_icon = Icon()
            new_icon.name = icon['signal']
            self.icons[icon['index'] - 1] = new_icon
        logger.debug(self.icons)

        for entity in data.get('entities', []):
            self.entities._load(**entity)
        self.entities.sort()

        self.parse_connections()

        for tile in data.get('tiles', []):
            self.tiles._load(**tile)
        self.tiles.sort()

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
            top_left, bottom_right = entity.top_left, entity.bottom_right
            _maxx, _minx, _maxy, _miny =\
                bottom_right.x, top_left.x, bottom_right.y, top_left.y
            if _maxx > maxx:
                maxx = int(_maxx)
            if _minx < minx:
                minx = int(_minx)
            if _maxy > maxy:
                maxy = int(_maxy)
            if _miny < miny:
                miny = int(_miny)
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
        logger.debug(len(self.connections))
        for entity in self.entities:
            connections = entity.get_connections()
