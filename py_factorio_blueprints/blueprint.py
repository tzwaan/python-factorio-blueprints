from py_factorio_blueprints import util
from py_factorio_blueprints.entity import Entity
from py_factorio_blueprints.util import Color, SignalID, Tile, Connection, Vector
import json


class OverlapException(Exception):
    pass


class Blueprint():
    class _Tiles():
        def __init__(self):
            self.grid = {}

        def __setitem__(self, key, value):
            if type(key) is Vector:
                x, y = key.xy
            else:
                x, y = key
            if y not in self.grid:
                self.grid[y] = {}
            self.grid[y][x] = value

        def __getitem__(self, key):
            if type(key) is Vector:
                x, y = key.xy
            else:
                x, y = key
            row = self.grid.get(y, {})
            tile = row.get(x, None)
            return tile

        def __delitem__(self, key):
            if type(key) is Vector:
                x, y = key.xy
            else:
                x, y = key
            if y not in self.grid:
                return
            if x not in self.grid[y]:
                return
            del(self.grid[y][x])

    def __init__(self, string=None, data=None, **kwargs):
        self.item = 'blueprint'
        self.label = ''
        self.label_color = None
        self.entities = []
        self.tile_list = []
        self.tiles = Blueprint._Tiles()
        self.icons = []
        self.version = 0

        self.entity_grid = {}

        if string is not None:
            data = util.decode(string)
        if data is not None:
            self.load(data)

    def __setitem__(self, key, value):
        if type(key) is Vector:
            x, y = key.xy
        else:
            x, y = key
        if y not in self.entity_grid:
            self.entity_grid[y] = {}
        self.entity_grid[y][x] = value

    def __getitem__(self, key):
        if type(key) is Vector:
            x, y = key.xy
        else:
            x, y = key
        row = self.entity_grid.get(y, {})
        entity = row.get(x, None)
        return entity

    def __delitem__(self, key):
        if type(key) is Vector:
            x, y = key.xy
        else:
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
            self.label_color = Color(label_color)
        self.version = data.get('version', 0)

        self.icons = [None, None, None, None]
        for icon in data.get('icons', []):
            # print('icon:', icon)
            self.icons[icon['index'] - 1] = SignalID(icon['signal'])
        # print(self.icons)

        for entity in data.get('entities', []):
            self.addEntity(Entity(self, entity))
        # print(self.entity_grid)

        self.parseConnections()

        for tile in data.get('tiles', []):
            self.addTile(Tile(tile))

    def setLabel(self, label, color=None):
        self.label = label
        if color is not None:
            self.label_color = Color(color)

    def addEntity(self, entity):
        self.entities.append(entity)
        if self.checkOverlap(entity):
            raise OverlapException
        entity.place()

    def addTile(self, tile):
        self.tile_list.append(tile)
        if self.checkOverlap(tile):
            raise OverlapException
        tile.place()

    def replaceEntities(self):
        self.entity_grid = {}
        for entity in self.entities:
            if self.checkOverlap(entity):
                raise OverlapException
            entity.place()

    def checkOverlap(self, obj):
        if type(obj) is Entity:
            for x, y in obj.coordinates:
                if self[(x, y)] is not None:
                    return True
            return False
        elif type(obj) is Tile:
            if self.tiles[(x, y)] is not None:
                return True
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

    def toJSON(self):
        obj = {}
        obj['item'] = self.item
        obj['label'] = self.label
        if self.label_color is not None:
            obj['label_color'] = self.label_color.toJSON()
        obj['entities'] = []
        for entity in self.entities:
            obj['entities'].append(entity.toJSON())
        obj['tiles'] = []
        for tile in self.tile_list:
            obj['tiles'].append(tile.toJSON())
        obj['icons'] = []
        for i, icon in enumerate(self.icons):
            if icon is not None:
                obj['icons'].append({'index': i + 1,
                                     'signal': icon.toJSON()})
        obj['version'] = self.version

        return {'blueprint': obj}

    def toJSONString(self):
        return json.dumps(self.toJSON())

    def toString(self):
        self.reIndexEntities()
        obj = self.toJSON()
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
                maxx = entity.position.x + offset.x
            elif entity.position.x - offset.x < minx:
                minx = entity.position.x - offset.x
            if entity.position.y + offset.y > maxy:
                maxy = entity.position.y + offset.y
            elif entity.position.y - offset.y < miny:
                miny = entity.position.y - offset.y
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
