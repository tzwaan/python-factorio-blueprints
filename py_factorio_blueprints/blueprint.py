from py_factorio_blueprints import util
from py_factorio_blueprints.entity import Entity as BaseEntity
from py_factorio_blueprints.util import Color, SignalID, Tile, Connection, Vector
from py_factorio_blueprints.entity_mixins import Rotatable, Items, Recipe, Container, Cargo
import json


class EntityOverlap(Exception):
    pass


class Blueprint:
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
        self.tiles = Blueprint._Tiles()
        self.icons = []
        self.version = 0

        self.entity_grid = {}

        if entity_mixins is None:
            entity_mixins = []
        self.__entity_mixins = entity_mixins

        print(string)
        if string is not None:
            data = util.decode(string)
            print(data)
        if data is not None:
            self.load(data)

        self._textures = textures
        if print2d:
            self.print2D()

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

    def load(self, data, **kwargs):
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
            mixins = util.namestr(entity["name"]).metadata.get("mixins", [])
            class Entity(BaseEntity, *mixins, *self.__entity_mixins):
                pass
            self.addEntity(Entity(**entity))
        # print(self.entity_grid)

        self.parseConnections()

        for tile in data.get('tiles', []):
            self.addTile(Tile(tile))

    def setLabel(self, label, color=None):
        self.label = label
        if color is not None:
            self.label_color = Color(**color)

    def addEntity(self, entity):
        entity.blueprint = self
        self.entities.append(entity)
        self.checkOverlap(entity)
        entity.place()

    def createEntity(self, name, position, direction,
                     *args, **kwargs):
        entity = self.Entity.createEntity(
            self, name, position, direction, *args, **kwargs)

        self.addEntity(entity)

    def addTile(self, tile):
        self.tile_list.append(tile)
        self.checkOverlap(tile)
        tile.place()

    def replaceEntities(self):
        self.entity_grid = {}
        for entity in self.entities:
            self.checkOverlap(entity)
            entity.place()

    def checkOverlap(self, obj):
        if not self.strict:
            return False
        if type(obj) is self.Entity:
            for x, y in obj.coordinates:
                if self[(x, y)] is not None:
                    raise EntityOverlap(x, y)
            return False
        elif type(obj) is Tile:
            if self.tiles[(x, y)] is not None:
                raise EntityOverlap(x, y)
            return False
        raise NotImplementedError

    def rotate(self, amount, around=Vector(0, 0), direction='clockwise'):
        amount %= 4
        if direction != 'clockwise':
            amount = 4 - amount
        for entity in self.entities:
            entity.rotate(amount, around=around)
        for tile in self.tile_list:
            tile.rotate(amount, around=around)
        self.replaceEntities()
        self.reIndexEntities()

    def to_json(self):
        obj = {}
        obj['item'] = self.item
        obj['label'] = self.label
        if self.label_color is not None:
            obj['label_color'] = self.label_color.to_json()
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

    def toString(self):
        self.reIndexEntities()
        obj = self.to_json()
        return util.encode(obj)

    def getEntityByID(self, entity_number):
        for entity in self.entities:
            if entity.entity_number == entity_number:
                return entity

    def reIndexEntities(self):
        self.entities.sort(key=lambda v: (v.position.y, v.position.x))
        index = 1
        for entity in self.entities:
            entity.entity_number = index
            index += 1

    @property
    def maximumValues(self):
        maxx, minx, maxy, miny = 0, 0, 0, 0
        for entity in self.entities:
            metadata = entity.name.metadata
            height = metadata.get('height', 1)
            width = metadata.get('width', 1)
            if entity.direction.isLeft or entity.direction.isRight:
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
        maxx, minx, maxy, miny = self.maximumValues
        return Vector((maxx + minx) / 2, (maxy + miny) / 2)

    @property
    def weightedCenter(self):
        center = Vector(0, 0)
        for entity in self.entities:
            center += entity.position
        center /= len(self.entities)
        return center

    @property
    def topLeft(self):
        maxx, minx, maxy, miny = self.maximumValues
        return Vector(minx, miny)

    @property
    def topRight(self):
        maxx, minx, maxy, miny = self.maximumValues
        return Vector(maxx, miny)

    @property
    def bottomLeft(self):
        maxx, minx, maxy, miny = self.maximumValues
        return Vector(minx, maxy)

    @property
    def bottomRight(self):
        maxx, minx, maxy, miny = self.maximumValues
        return Vector(maxx, maxy)

    @property
    def corners(self):
        maxx, minx, maxy, miny = self.maximumValues
        return (
            Vector(minx, miny), Vector(maxx, miny),
            Vector(minx, maxy), Vector(maxx, maxy))

    def reCenter(self, around=None):
        if around is not None:
            center = around
        else:
            center = self.center.ceil()
        if center == Vector(0, 0):
            return
        for entity in self.entities:
            entity.position -= center
        self.replaceEntities()

    def parseConnections(self):
        self.connections = []
        for entity in self.entities:
            if entity.raw_connections is not None:
                for side, connection_point in \
                        entity.raw_connections.items():
                    for color, connections in connection_point.items():
                        for connection in connections:
                            other = self.getEntityByID(
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
            connections = entity.getConnections()

    def print2D(self, textures=None):
        """
        Print a 2d representation of the blueprint using unicode
        characters as specified.

        :Param textures: A dictionary containg specific characters for
                         specific entities. Check examples for more info.
        """
        if textures is None:
            textures = self._textures
        topLeft, topRight, bottomLeft, bottomRight = self.corners
        result = "\n"
        for y in range(topLeft.y, bottomLeft.y + 1):
            for x in range(topLeft.x, topRight.x + 1):
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
