from py_factorio_blueprints.util import Vector, namestr, Color, Connection
from py_factorio_blueprints.entity_mixins import BaseMixin


class Direction(int):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

    def __new__(cls, value):
        return int.__new__(cls, value % 8)

    def __add__(self, other):
        return Direction(
            super().__add__(other))

    def __sub__(self, other):
        return Direction(
            super().__sub__(other))

    def __div__(self, other):
        return Direction(
            super().__div__(other))

    def __repr__(self):
        dirs = (
            "Up", "Up-Right", "Right", "Down-Right",
            "Down", "Down-Left", "Left", "Up-Left"
        )
        return "<Direction ({dir})>".format(dir=dirs[self])

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
    def isUp(self):
        return self == 0

    @property
    def isRight(self):
        return self == 2

    @property
    def isDown(self):
        return self == 4

    @property
    def isLeft(self):
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


class CombinatorControl:
    def __init__(self, first, operator, second, output, type="arithmetic"):
        self.type = type
        self.operator = operator
        self.first = first
        self.second = second
        self.output = output

    @classmethod
    def from_entity_data(cls, data):
        type = data["name"][0:-11]
        control_behavior = data.get("control_behavior", None)
        if control_behavior is None:
            return None
        condition_data = control_behavior.get("{}_conditions".format(type), None)
        if condition_data is None:
            return None
        operator = condition_data["operation"]\
            if type == "arithmetic" else condition_data["comparator"]
        def get_from(data, key):
            value = data.get("{}_constant".format(key), None)
            if value is None:
                value = data.get("{}_signal".format(key))["name"]
            return value
        first = get_from(condition_data, "first")
        second = get_from(condition_data, "second")
        output = get_from(condition_data, "output")

        return cls(first, operator, second, output, type=type)

    @property
    def first(self):
        return self.__first

    @first.setter
    def first(self, value):
        if isinstance(value, int):
            self.__first = value
        else:
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
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = namestr(value)

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value not in ["arithmetic", "decider"]:
            raise ValueError(value)
        self.__type = value

    @property
    def operator(self):
        return self.__operator

    @operator.setter
    def operator(self, value):
        if self.type == "arithmetic":
            operators = ["*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"]
        else:
            operators = [">", "<", "=", ">=", "<=", "!="]
        if value not in operators:
            raise ValueError("{} not in {}".format(value, operators))
        self.__operator = value

    def to_json(self):
        control_behavior = {}
        for slot in ["first", "second"]:
            if isinstance(getattr(self, slot), int):
                control_behavior["{}_constant".format(slot)] = getattr(self, slot)
            else:
                control_behavior["{}_signal".format(slot)] = {
                    "type": getattr(self, slot).metadata["type"],
                    "name": getattr(self, slot)
                }
        control_behavior["output_signal"] = {
            "type": self.output.metadata["type"],
            "name": self.output
        }
        control_behavior["operation" if self.type == "arithmetic" else "comparator"] = self.operator
        result = {
            "{}_conditions".format(self.type): control_behavior
        }
        return result


class Entity(BaseMixin):
    def __repr__(self):
        return '<Entity (name: "{name}", position: {pos}, direction: {dir})>'.format(
            name=self.name,
            pos=self.position,
            dir=self.direction)

    def __str__(self):
        return '<Entity (name: "{name}")>'.format(
            name=self.name)

    @classmethod
    def createEntity(cls, name, position, direction,
                     *args, **kwargs):
        data = {
            "name": name,
            "position": position,
            "direction": direction
        }
        return cls(data, *args, **kwargs)

    def __init__(self, *args, name, position, direction=0, entity_number=None, **kwargs):
        self.blueprint = None
        self.entity_number = entity_number
        self.name = name
        self.position = position
        self.direction = direction

        self.width = self.name.metadata["width"]
        self.height = self.name.metadata["height"]

        if self.direction.isLeft or self.direction.isRight:
            self.height, self.width = self.width, self.height

        self.raw_connections = kwargs.pop('connections', None)
        # self.connections = []

        self.control_behavior = CombinatorControl.from_entity_data({**{"name": self.name}, **kwargs})

        self.parameters = kwargs.pop('parameters', None)
        self.alert_parameters = kwargs.pop('alert_parameters', None)

        self.auto_launch = kwargs.pop('auto_launch', None)

        self.variation = kwargs.pop('variation', None)
        color = kwargs.pop('color', None)
        if color is not None:
            self.color = Color(**color)
        else:
            self.color = None
        self.station = kwargs.pop('station', None)

        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = namestr(value)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = Vector(value)

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        self.__direction = Direction(value)

    @property
    def blueprint(self):
        return self.__blueprint

    @blueprint.setter
    def blueprint(self, value):
        self.__blueprint = value

    def getConnections(self):
        connections = [connection.orientate(self)
                       for connection in self.blueprint.connections
                       if connection.attachedTo(self)]
        return connections

    def connect(
            self,
            to_entity,
            from_side='in',
            to_side='in',
            color='red'):
        conn = Connection(self, to_entity, from_side, to_side, color)
        if conn not in self.blueprint.connections:
            self.blueprint.connections.append(conn)
        return conn

    def connectionsto_json(self):
        connections = self.getConnections()
        obj = {}
        for connection in connections:
            if connection.from_side not in obj:
                obj[connection.from_side] = {}
            if connection.color not in obj[connection.from_side]:
                obj[connection.from_side][connection.color] = []

            obj[connection.from_side][connection.color].append({
                'entity_id': connection.to_entity.entity_number,
                'circuit_id': connection.to_side})
        return obj

    @property
    def coordinates(self):
        metadata = self.name.metadata
        height = metadata.get('height', 1)
        width = metadata.get('width', 1)
        if self.direction.isLeft or self.direction.isRight:
            height, width = width, height
        topleft = self.topLeft
        for y in range(
                int(topleft.y),
                int(topleft.y) + height):
            for x in range(
                    int(topleft.x),
                    int(topleft.x) + width):
                yield Vector(x, y)

    @property
    def topLeft(self):
        offset = Vector(
            (self.width - 1) / 2.0,
            (self.height - 1) / 2.0)
        return self.position - offset

    @property
    def topRight(self):
        offset = Vector(
            - (self.width - 1) / 2.0,
            (self.height - 1) / 2.0)
        return self.position - offset

    @property
    def bottomLeft(self):
        offset = Vector(
            (self.width - 1) / 2.0,
            - (self.height - 1) / 2.0)
        return self.position - offset

    @property
    def bottomRight(self):
        offset = Vector(
            - (self.width - 1) / 2.0,
            (self.height - 1) / 2.0)
        return self.position - offset

    def getTextureIndex(self, position):
        x, y = position - self.topLeft
        return Vector(int(x), int(y))

    def place(self):
        for x, y in self.coordinates:
            self.blueprint[(x, y)] = self

    def rotate(
            self,
            amount,
            around=Vector(0, 0),
            direction=Direction.CLOCKWISE):

        position = self.position - around
        amount %= 4
        if direction != Direction.CLOCKWISE:
            amount = 4 - amount

        def r(v):
            return Vector(-v.y, v.x)

        for _ in range(amount):
            position = r(position)
            self.width, self.height = self.height, self.width
        self.position = position + around

        mixin = super()
        if hasattr(mixin, "rotate"):
            mixin.rotate(amount)

    def to_json(self):
        obj = super().to_json()
        obj['entity_number'] = self.entity_number
        obj['name'] = str(self.name)
        obj['position'] = self.position.to_json()
        connections = self.connectionsto_json()
        if connections != {}:
            obj['connections'] = connections

        if self.control_behavior is not None:
            obj['control_behavior'] = self.control_behavior.to_json()
        if self.parameters is not None:
            obj['parameters'] = self.parameters
        if self.alert_parameters is not None:
            obj['alert_parameters'] = self.alert_parameters
        if self.auto_launch is not None:
            obj['auto_launch'] = self.auto_launch
        if self.variation is not None:
            obj['variation'] = self.variation
        if self.color is not None:
            obj['color'] = self.color.to_json()
        if self.station is not None:
            obj['station'] = self.station

        return obj

