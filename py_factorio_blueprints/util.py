import json
import zlib
import base64
import math
from py_factorio_blueprints.exceptions import *


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
    def __init__(self, *args, **kwargs):
        props = ['r', 'g', 'b', 'a']
        for prop in props:
            setattr(self, prop, 1)

        if args:
            if len(args) > 4:
                raise TypeError(
                    f'Color() takes a maximum of 4 positional '
                    f'arguments ({len(args)} given)')
            for i, arg in enumerate(args):
                setattr(self, props[i], arg)
        if 'r' in kwargs:
            self.r = kwargs['r']
        if 'g' in kwargs:
            self.g = kwargs['g']
        if 'b' in kwargs:
            self.b = kwargs['b']
        if 'a' in kwargs:
            self.a = kwargs['a']

    def __repr__(self):
        return f"<Color (r:{self.r}, g:{self.g}, b:{self.b}, a:{self.a})>"

    def __iter__(self):
        yield from [self.r, self.g, self.b, self.a]

    def __eq__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return (
            self.r == other.r and
            self.g == other.g and
            self.b == other.b and
            self.a == other.a)

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


class Direction(int):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

    def __new__(cls, value):
        return super().__new__(cls, value % 8)

    def __add__(self, other):
        return Direction(
            super().__add__(other))

    def __sub__(self, other):
        return Direction(
            super().__sub__(other))

    def __floordiv__(self, other):
        return NotImplemented

    def __truediv__(self, other):
        return NotImplemented

    def __repr__(self):
        dirs = (
            "Up", "Up-Right", "Right", "Down-Right",
            "Down", "Down-Left", "Left", "Up-Left"
        )
        return f"<Direction ({dirs[self]})>"

    def __str__(self):
        return str(int(self))

    @classmethod
    def up(cls):
        return cls(0)

    @classmethod
    def right(cls):
        return cls(2)

    @classmethod
    def down(cls):
        return cls(4)

    @classmethod
    def left(cls):
        return cls(6)

    @property
    def is_up(self):
        return self == 0

    @property
    def is_right(self):
        return self == 2

    @property
    def is_down(self):
        return self == 4

    @property
    def is_left(self):
        return self == 6

    def rotate45(self, amount, direction=CLOCKWISE):
        """rotates by 45 degrees"""
        if direction != self.CLOCKWISE:
            amount = 8 - amount
        return Direction(self + amount)

    def rotate(self, amount, direction=CLOCKWISE):
        """rotates by 90 degrees"""
        amount *= 2
        if direction != self.CLOCKWISE:
            amount = 8 - amount
        return Direction(self + amount)

    @property
    def vector(self):
        if self == 0:
            return Vector(0, -1)
        elif self == 1:
            return Vector(1, -1)
        elif self == 2:
            return Vector(1, 0)
        elif self == 3:
            return Vector(1, 1)
        elif self == 4:
            return Vector(0, 1)
        elif self == 5:
            return Vector(-1, 1)
        elif self == 6:
            return Vector(-1, 0)
        elif self == 7:
            return Vector(-1, -1)
        return ValueError("Direction outside of 0-7 range")


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
        self.__first = NameStr(value)

    @property
    def second(self):
        return self.__second

    @second.setter
    def second(self, value):
        if isinstance(value, int):
            self.__second = value
        else:
            self.__second = NameStr(value)

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


class NameStr(str):
    def __new__(cls, value):
        from py_factorio_blueprints.defaultentities import \
            defaultentities as entity_data
        if value is None:
            return None
        if not entity_data.get(value, None):
            raise UnknownEntity(value)
        return super().__new__(cls, value)

    @property
    def metadata(self):
        from py_factorio_blueprints.defaultentities import \
            defaultentities as entity_data
        return entity_data.get(self)

    @property
    def type(self):
        from py_factorio_blueprints.defaultentities import \
            defaultentities as entity_data
        return entity_data.get(self)["type"]


class SignalID:
    def __init__(self, data):
        self.name = NameStr(data['name'])

    @property
    def type(self):
        from py_factorio_blueprints.defaultentities import \
            defaultentities as entity_data
        return entity_data[self.name]['type']

    def __repr__(self):
        return f"<SignalID ({self.name}, type: {self.type})>"

    def to_json(self):
        return {'name': self.name,
                'type': self.type}


class Connection:
    def __init__(self, from_entity, to_entity,
                 from_side=1, to_side=1, color='green'):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.from_side = int(from_side)
        self.to_side = int(to_side)
        self.color = color

    def __repr__(self):
        return f"<Connection ({self.color} " \
               f"from:({self.from_entity}, {self.from_side}) " \
               f"to:({self.to_entity}, {self.to_side}))>"

    def attached_to(self, entity):
        if self.from_entity is entity or self.to_entity is entity:
            return True
        return False

    def flip(self):
        self.from_entity, self.to_entity = self.to_entity, self.from_entity
        self.from_side, self.to_side = self.to_side, self.from_side

    def orientate(self, entity):
        if self.to_entity == entity:
            self.flip()
        return self

    def flip_color(self):
        if self.color == 'green':
            self.color = 'red'
        else:
            self.color = 'green'

    def __eq__(self, other):
        if type(other) is not Connection:
            return NotImplemented
        if self.color != other.color:
            return False
        if self.from_entity == other.from_entity and \
                self.to_entity == other.to_entity and \
                self.from_side == other.from_side and \
                self.to_side == other.to_side:
            return True
        elif self.from_entity == other.to_entity and \
                self.to_entity == other.from_entity and \
                self.from_side == other.to_side and \
                self.to_side == other.from_side:
            return True
        return False


class Vector:
    def __new__(cls, *args, **kwargs):
        if args and kwargs:
            raise TypeError("Vector() can't set both args and kwargs")
        if not args and not kwargs:
            return None
        if args:
            if args[0] is None:
                return None
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        if args:
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
        else:
            self.x = kwargs['x']
            self.y = kwargs['y']

    def to_json(self):
        return {
            'x': self.x,
            'y': self.y
        }

    def __iter__(self):
        yield from [self.x, self.y]

    @property
    def xy(self):
        return Vector(self.x, self.y)

    @property
    def yx(self):
        return Vector(self.y, self.x)

    def __repr__(self):
        return f"<Vector ({self.x}, {self.y})>"

    def __add__(self, other):
        if type(other) is Vector:
            return Vector(self.x + other.x, self.y + other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x + other, self.y + other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x + x, self.y + y)
        return NotImplemented

    def __radd__(self, other):
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
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x / x, self.y / y)
        return NotImplemented

    def __rtruediv__(self, other):
        if type(other) is int or type(other) is float:
            return Vector(other / self.x, other / self.y)
        elif type(other) is tuple:
            x, y = other
            return Vector(x / self.x, y / self.y)
        return NotImplemented

    def __floordiv__(self, other):
        if type(other) is Vector:
            return Vector(self.x // other.x, self.y // other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x // other, self.y // other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x // x, self.y // y)
        return NotImplemented

    def __rfloordiv__(self, other):
        if type(other) is int or type(other) is float:
            return Vector(other // self.x, other // self.y)
        elif type(other) is tuple:
            x, y = other
            return Vector(x // self.x, y // self.y)
        return NotImplemented

    def __mod__(self, other):
        if type(other) is Vector:
            return Vector(self.x % other.x, self.y % other.y)
        elif type(other) is int or type(other) is float:
            return Vector(self.x % other, self.y % other)
        elif type(other) is tuple:
            x, y = other
            return Vector(self.x % x, self.y % y)
        return NotImplemented

    def __rmod__(self, other):
        if type(other) is int:
            return Vector(other % self.x, other % self.y)
        elif type(other) is tuple:
            x, y = other
            return Vector(x % self.x, y % self.y)

    def __eq__(self, other):
        if type(other) is tuple:
            x, y = other
            if self.x == x and self.y == y:
                return True
            else:
                return False
        elif type(other) is not Vector:
            return NotImplemented
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __lt__(self, other):
        if type(other) is tuple:
            other = Vector(other)
        elif type(other) is not Vector:
            return NotImplemented
        if self.x < other.x and self.y < other.y:
            return True
        return False

    def __gt__(self, other):
        if type(other) is tuple:
            other = Vector(other)
        elif type(other) is not Vector:
            return NotImplemented
        if self.x > other.x and self.y > other.y:
            return True
        return False

    def ceil(self):
        x = math.ceil(self.x)
        y = math.ceil(self.y)
        return Vector(x, y)

    def floor(self):
        x = math.floor(self.x)
        y = math.floor(self.y)
        return Vector(x, y)

    def round(self):
        x = math.floor(self.x + 0.5)
        y = math.floor(self.y + 0.5)
        return Vector(x, y)

    def copy(self):
        return Vector(self.x, self.y)

    def rotate(self, amount):
        amount %= 4
        v = self.copy()
        for _ in range(amount):
            v.x, v.y = -v.y, v.x
        return v


class TileName:
    class NameStr(str):
        @property
        def data(self):
            from py_factorio_blueprints import Blueprint
            return Blueprint.tile_prototypes[self]

    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        if not getattr(instance, 'strict', True):
            setattr(instance, self.name, value)
            return

        from py_factorio_blueprints.blueprint import Blueprint

        if value not in Blueprint.tile_prototypes:
            raise UnknownTile(value)
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return TileName.NameStr(getattr(instance, self.name, ""))


class Tile:
    name = TileName()

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self.position = Vector(kwargs.pop('position'))
        super().__init__(*args, **kwargs)

    def to_json(self):
        return {'name': self.name,
                'position': self.position.to_json()}

    def top_left(self):
        return self.position - Vector(0.5, 0.5)

    def bottom_right(self):
        return self.position + Vector(0.5, 0.5)

    def collides(self, position):
        return self.top_left < position < self.bottom_right

    def rotate(self, amount, around=None, direction='clockwise'):
        if around is None:
            around = Vector(0, 0)
        position = self.position - around
        amount %= 4
        if direction != 'clockwise':
            amount = 4 - amount

        def r(v):
            return Vector(-v.y, v.x)

        for _ in range(amount):
            position = r(position)
        self.position = position + around


def obj_set(obj, key, value):
    if value is None:
        return

    to_json = getattr(value, "to_json", None)
    if callable(to_json):
        value = to_json()
        if value is None:
            return

    obj[key] = value
    return obj


class ControlBehaviorMeta(type):
    def __new__(mcs, name, bases, attrs):
        control_behavior = attrs.pop('ControlBehavior', None)
        new_cls = super().__new__(mcs, name, bases, attrs)

        control_behaviors = [
            control_behavior,
            *[getattr(base, 'ControlBehavior', None)
              for base in bases]]
        control_behaviors = tuple(x for x in control_behaviors if x is not None)

        if control_behaviors:
            control_behavior = type(
                'ControlBehavior',
                control_behaviors,
                {})
            new_cls.ControlBehavior = control_behavior

        return new_cls
