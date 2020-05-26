import json
import zlib
import base64
import math


class InvalidExchangeString(Exception):
    pass


class UnknownEntity(Exception):
    pass


def _decode_0(string):
    try:
        data = json.loads(
            zlib.decompress(
                base64.b64decode(string[1:])).decode('UTF-8'))
    except (TypeError, base64.binascii.Error, zlib.error):
        raise InvalidExchangeString(
            "Could not decode exchange string")
    return data


def _encode_0(obj):
    temp = bytes(json.dumps(obj), 'UTF-8')
    temp2 = zlib.compress(temp)
    temp3 = base64.b64encode(temp2)
    return '0' + temp3.decode('UTF-8')


def decode(string):
    return _decode[string[0]](string)


def encode(obj):
    return _encode['latest'](obj)


_decode = {
    '0': _decode_0
}

_encode = {
    '0': _encode_0
}

_decode['latest'] = _decode['0']
_encode['latest'] = _encode['0']


class Color:
    def __init__(self, **kwargs):
        self.r = kwargs.get('r', 1)
        self.g = kwargs.get('g', 1)
        self.b = kwargs.get('b', 1)
        self.a = kwargs.get('a', 1)

    def __repr__(self):
        return "<Color (r:{}, g:{}, b:{}, a:{})>".format(self.r, self.g, self.b, self.a)

    def __iter__(self):
        yield from [self.r, self.g, self.g, self.a]

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        self._r = max(min(1, value), 0)

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        self._g = max(min(1, value), 0)

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = max(min(1, value), 0)

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self._a = max(min(1, value), 0)

    def to_json(self):
        obj = {
            'r': self.r,
            'g': self.g,
            'b': self.b,
            'a': self.a
        }
        return obj


class Condition:
    def __init__(self, *, first_signal=None, comparator=None,
                 constant=None, second_signal=None):
        if "name" in first_signal:
            first_signal = first_signal["name"]
        self.first = first_signal
        self.second = second_signal or constant
        self.comparator = comparator

    @property
    def first(self):
        return self.__first

    @first.setter
    def first(self, value):
        self.__first = namestr(value)

    @property
    def second(self):
        return self.__second

    @second.setter
    def second(self, value):
        if isinstance(value, int):
            self.__second = value
        else:
            self.__second = namestr(value)

    @property
    def comparator(self):
        return self.__comparator

    @comparator.setter
    def comparator(self, value):
        if value not in [">", "<", "=", ">=", "<=", "!="]:
            raise ValueError(value)
        self.__comparator = value

    def to_json(self):
        condition = {}
        if self.first is not None:
            condition["first_signal"] = {
                "name": self.first,
                "type": self.first.type}
        condition["comparator"] = self.comparator
        if self.second is not None:
            if isinstance(self.second, int):
                condition["constant"] = self.second
            else:
                condition["second_signal"] = {
                    "name": self.second,
                    "type": self.second.type}
        return condition


class namestr(str):
    def __new__(cls, value):
        from py_factorio_blueprints.defaultentities import defaultentities as entity_data
        if value is None:
            return None
        if not entity_data.get(value, None):
            raise UnknownEntity(value)
        return super().__new__(cls, value)

    @property
    def metadata(self):
        from py_factorio_blueprints.defaultentities import defaultentities as entity_data
        return entity_data.get(self)

    @property
    def type(self):
        from py_factorio_blueprints.defaultentities import defaultentities as entity_data
        return entity_data.get(self)["type"]


class SignalID():
    def __init__(self, data):
        self.name = namestr(data['name'])

    @property
    def type(self):
        from py_factorio_blueprints.defaultentities import defaultentities as entity_data
        return entity_data[self.name]['type']

    def __repr__(self):
        return "<SignalID ({}, type: {})>".format(self.name, self.type)

    def to_json(self):
        return {'name': self.name,
                'type': self.type}


class Connection():
    def __init__(self, from_entity, to_entity,
                 from_side=1, to_side=1, color='green'):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.from_side = int(from_side)
        self.to_side = int(to_side)
        self.color = color

    def __repr__(self):
        return "<Connection ({} from:({}, {}) to:({}, {}))>".format(self.color,
                                                                    self.from_entity,
                                                                    self.from_side,
                                                                    self.to_entity,
                                                                    self.to_side)

    def attachedTo(self, entity):
        if self.from_entity == entity or self.to_entity == entity:
            return True
        return False

    def flip(self):
        self.from_entity, self.to_entity = self.to_entity, self.from_entity
        self.from_side, self.to_side = self.to_side, self.from_side

    def orientate(self, entity):
        if self.to_entity == entity:
            self.flip()
        return self

    def flipColor(self):
        if self.color == 'green':
            self.color = 'red'
        else:
            self.color = 'green'

    def __eq__(self, other):
        if type(other) is not Connection:
            return NotImplemented
        if self.color != other.color:
            return False
        if self.from_entity == other.from_entity and self.to_entity == other.to_entity and self.from_side == other.from_side and self.to_side == other.to_side:
            return True
        elif self.from_entity == other.to_entity and self.to_entity == other.from_entity and self.from_side == other.to_side and self.to_side == other.from_side:
            return True
        return False


class Vector:
    def __new__(cls, *args):
        if args[0] is None:
            return None
        return super().__new__(cls)

    def __init__(self, *args):
        if len(args) == 1:
            if type(args[0]) == dict:
                self.x = args[0]["x"]
                self.y = args[0]["y"]
            elif type(args[0]) == tuple or \
                    type(args[0]) == Vector:
                self.x, self.y = args[0]
            else:
                raise ValueError(args)
        elif len(args) == 2:
            self.x = args[0]
            self.y = args[1]
        else:
            raise ValueError(args)

    def to_json(self):
        obj = {}
        obj['x'] = self.x
        obj['y'] = self.y
        return obj

    def __iter__(self):
        yield from [self.x, self.y]

    @property
    def xy(self):
        return self.x, self.y

    @classmethod
    def fromObject(cls, data):
        if type(data) is tuple:
            x, y = data
        elif type(data) is list:
            if len(data) >= 2:
                x, y = data[0], data[1]
            else:
                raise NotImplementedError
        elif type(data) is dict:
            x, y = data['x'], data['y']
        else:
            raise NotImplementedError
        return cls(x, y)

    def __repr__(self):
        return "<Vector ({}, {})>".format(self.x, self.y)

    def __add__(self, other):
        if type(other) is Vector:
            return Vector(self.x + other.x, self.y + other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x + other, self.y + other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x + x, self.y + y)
        return NotImplemented

    def _radd(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) is Vector:
            return Vector(self.x - other.x, self.y - other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x - other, self.y - other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x - x, self.y - y)
        return NotImplemented

    def __rsub__(self, other):
        if type(other) is int or type(other) is float:
            return Vector(other - self.x, other - self.y)
        elif type(other) is tuple:
            x, y = other
            return Vector(x - self.x, y - self.y)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is Vector:
            return Vector(self.x * other.x, self.y * other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x * other, self.y * other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x * x, self.y * y)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) is Vector:
            return Vector(self.x / other.x, self.y / other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x / other, self.y / other)
        return NotImplemented

    def __rtruediv__(self, other):
        if type(other) is int or type(other) is float:
            return Vector(other / self.x, other / self.y)
        return NotImplemented

    def __floordiv__(self, other):
        if type(other) is Vector:
            return Vector(self.x // other.x, self.y // other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x // other, self.y // other)
        return NotImplemented

    def __rfloordiv__(self, other):
        if type(other) is int or type(other) is float:
            return Vector(other // self.x, other // self.y)
        return NotImplemented

    def __mod__(self, other):
        if type(other) is Vector:
            return Vector(self.x % other.x, self.y % other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x % other, self.y % other)
        return NotImplemented

    def __eq__(self, other):
        if type(other) is not Vector:
            return NotImplemented
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def ceil(self):
        self.x = math.ceil(self.x)
        self.y = math.ceil(self.y)
        return self

    def copy(self):
        return Vector(self.x, self.y)

    def rotate(self, amount):
        amount %= 4
        v = self.copy()
        for _ in range(amount):
            v.x, v.y = -v.y, v.x
        return v


class Tile():
    def __init__(self, data):
        self.name = namestr(data['name'])
        self.position = Vector(data['position']['x'], data['position']['y'])

    def to_json(self):
        return {'name': self.name,
                'position': self.position.to_json()}

    def rotate(self, amount, around=Vector(0, 0), direction='clockwise'):
        position = self.position - around
        amount %= 4
        if direction != 'clockwise':
            amount = 4 - amount

        def r(v):
            return Vector(-v.y, v.x)

        for _ in range(amount):
            position = r(position)
        self.position = position + around
