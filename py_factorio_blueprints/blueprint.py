from py_factorio_blueprints import util
from py_factorio_blueprints.entity import Entity as BaseEntity
from py_factorio_blueprints.util import (
    Color, SignalID, Tile, Connection, Vector, obj_set
)
from py_factorio_blueprints.entity_mixins import (
    Rotatable, Items, Recipe, Container, Cargo
)
import json


class EntityOverlap(Exception):
    pass


class Blueprint:
    entity_prototypes = {}
    recipe_prototypes = {}

    @classmethod
    def set_entity_data(cls, data, append=False):
        if append:
            data = {**cls.entity_prototypes, **data}
        cls.entity_prototypes = data

    @classmethod
    def set_recipe_data(cls, data, append=False):
        if append:
            data = {**cls.recipe_prototypes, **data}
        cls.recipe_prototypes = data

    @classmethod
    def import_prototype_data(cls, filename, **kwargs):
        with open(filename) as f:
            data = json.load(f)
            cls.set_entity_data(data['entity'], **kwargs)
            cls.set_recipe_data(data['recipe'], **kwargs)

    class _Tiles:
        def __init__(self):
            self.grid = {}

        def __setitem__(self, key, value):
            x, y = key
            if y not in self.grid:
                self.grid[y] = {}
            self.grid[y][x] = value

        def __getitem__(self, key):
            x, y = key
            row = self.grid.get(y, {})
            tile = row.get(x, None)
            return tile

        def __delitem__(self, key):
            x, y = key
            if y not in self.grid:
                return
            if x not in self.grid[y]:
                return
            del(self.grid[y][x])

    def __init__(self, string=None, data=None,
                 *, print2d=False, textures=None,
                 entity_mixins=None, strict=False, **kwargs):
        if textures is None:
            textures = {'empty': " ", 'unknown': "X"}
        super().__init__(**kwargs)
        self.strict = strict
        self.item = 'blueprint'
        self.label = ''
        self.label_color = None
        self.entities = []
        self.tile_list = []
        self.tiles = self._Tiles()
        self.icons = []
        self.version = 0
        self.connections = []

        self.entity_grid = {}
        self.__entity_mixins = entity_mixins or []

        print(string)
        if string is not None:
            data = util.decode(string)
            print(data)
        if data is not None:
            self.load(data)

        self._textures = textures
        if print2d:
            self.print_2d()

    def __setitem__(self, key, value):
        x, y = key
        if y not in self.entity_grid:
            self.entity_grid[y] = {}
        self.entity_grid[y][x] = value

    def __getitem__(self, key):
        x, y = key
        row = self.entity_grid.get(y, {})
        entity = row.get(x, None)
        return entity

    def __delitem__(self, key):
        x, y = key
        if y not in self.entity_grid:
            return
        if x not in self.entity_grid[y]:
            return
        del(self.entity_grid[y][x])

    def load(self, data):
        if 'blueprint' in data:
            data = data['blueprint']
        # print(data)

        self.item = data.get('item', 'blueprint')
        self.label = data.get('label', 'My Blueprint')
        label_color = data.get('label_color', None)
        if label_color is not None:
            self.label_color = Color(**label_color)
        self.version = data.get('version', 0)

        self.icons = [None, None, None, None]
        for icon in data.get('icons', []):
            # print('icon:', icon)
            self.icons[icon['index'] - 1] = SignalID(icon['signal'])
        # print(self.icons)

        for entity in data.get('entities', []):
            print(entity)
            mixins = util.NameStr(entity["name"]).metadata.get("mixins", [])
            entity_mixins = self.__entity_mixins

            class Entity(BaseEntity, *mixins, *entity_mixins):
                pass

            self.add_entity(Entity(**entity))
        # print(self.entity_grid)

        self.parse_connections()

        for tile in data.get('tiles', []):
            self.add_tile(Tile(tile))

    def set_label(self, label, color=None):
        self.label = label
        if isinstance(color, Color):
            self.label_color = color
        elif color is not None:
            self.label_color = Color(**color)

    def add_entity(self, entity):
        entity.blueprint = self
        self.entities.append(entity)
        self.check_overlap(entity)
        entity.place()

    def create_entity(self, name, position, direction,
                      *args, **kwargs):
        entity = self.Entity.create_entity(
            self, name, position, direction, *args, **kwargs)

        self.add_entity(entity)

    def add_tile(self, tile):
        self.tile_list.append(tile)
        self.check_overlap(tile)
        tile.place()

    def replace_entities(self):
        self.entity_grid = {}
        for entity in self.entities:
            self.check_overlap(entity)
            entity.place()

    def check_overlap(self, obj):
        if not self.strict:
            return False
        if type(obj) is self.Entity:
            grid = self
        elif type(obj) is Tile:
            grid = self.tiles
        else:
            raise NotImplementedError

        for x, y in obj.coordinates:
            if grid[(x, y)] is not None:
                raise EntityOverlap(x, y)
        return False

    def rotate(self, amount, around=Vector(0, 0), direction='clockwise'):
        amount %= 4
        if direction != 'clockwise':
            amount = 4 - amount
        for entity in self.entities:
            entity.rotate(amount, around=around)
        for tile in self.tile_list:
            tile.rotate(amount, around=around)
        self.replace_entities()
        self.reindex_entities()

    def to_json(self):
        obj = {
            'item': self.item,
            'label': self.label
        }
        obj_set(obj, 'label_color', self.label_color)
        obj['entities'] = []
        for entity in self.entities:
            obj['entities'].append(entity.to_json())
        obj['tiles'] = []
        for tile in self.tile_list:
            obj['tiles'].append(tile.to_json())
        obj['icons'] = []
        for i, icon in enumerate(self.icons):
            if icon is not None:
                obj['icons'].append({'index': i + 1,
                                     'signal': icon.to_json()})
        obj['version'] = self.version

        return {'blueprint': obj}

    def to_json_string(self):
        return json.dumps(self.to_json())

    def to_string(self):
        self.reindex_entities()
        obj = self.to_json()
        return util.encode(obj)

    def get_entity_by_id(self, entity_number):
        for entity in self.entities:
            if entity.entity_number == entity_number:
                return entity

    def reindex_entities(self):
        self.entities.sort(key=lambda v: (v.position.y, v.position.x))
        index = 1
        for entity in self.entities:
            entity.entity_number = index
            index += 1

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
