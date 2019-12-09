from py_factorio_blueprints.util import Vector, namestr, Color, Connection


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


class Entity():
    def __repr__(self):
        return '<Entity (name: "{name}", position: {pos}, direction: {dir})>'.format(
            name=self.name,
            pos=self.position,
            dir=self.direction)

    def __str__(self):
        return '<Entity (name: "{name}")>'.format(
            name=self.name)

    @classmethod
    def createEntity(cls, blueprint,
                     name, position, direction,
                     *args, **kwargs):
        data = {
            "name": name,
            "position": position,
            "direction": direction
        }
        return cls(blueprint, data, *args, **kwargs)

    def __init__(self, blueprint, data, *args, **kwargs):
        self.blueprint = blueprint
        self.entity_number = data.get('entity_number', None)
        self.name = namestr(data['name'])
        if type(data['position']) is Vector:
            self.position = data['position']
        else:
            self.position = Vector(
                data['position']['x'],
                data['position']['y'])
        self.direction = Direction(data.get('direction', 0))

        self.width = self.name.metadata["width"]
        self.height = self.name.metadata["height"]

        if self.direction.isLeft or self.direction.isRight:
            self.height, self.width = self.width, self.height

        self.raw_connections = data.get('connections', None)
        # self.connections = []

        self.control_behavior = data.get('control_behavior', None)

        self.items = data.get('items', None)
        self.recipe = namestr(data.get('recipe', None))
        self.bar = data.get('bar', None)

        self.infinity_settings = data.get('infinity_settings', None)

        self.type = data.get('type', None)
        self.input_priority = data.get('input_priority', None)
        self.output_priority = data.get('output_priority', None)
        self.filter = data.get('filter', None)
        self.filters = data.get('filters', None)
        self.filter_mode data.get('filter_mode', None)

        self.override_stack_size = data.get('override_stack_size', None)

        drop_position = data.get('drop_position', None)
        if drop_position:
            self.drop_position = Vector(
                drop_position['x'],
                drop_position['y'])
        else:
            self.drop_position = None
        pickup_position = data.get('pickup_position', None)
        if pickup_position:
            self.pickup_position = Vector(
                pickup_position['x'],
                pickup_position['y'])
        else:
            self.pickup_position = None

        self.request_filters = data.get(
            'request_filters', None)
        self.request_from_buffers = data.get(
            'request_from_buffers', None)

        self.parameters = data.get('parameters', None)
        self.alert_parameters = data.get('alert_parameters', None)

        self.auto_launch = data.get('auto_launch', None)

        self.variation = data.get('variation', None)
        color = data.get('color', None)
        if color is not None:
            self.color = Color(**color)
        else:
            self.color = None
        self.station = data.get('station', None)

        super().__init__(*args, **kwargs)

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

    def connectionsToJSON(self):
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
        self.direction = self.direction.rotate(amount)

    def toJSON(self):
        obj = {}
        obj['entity_number'] = self.entity_number
        obj['name'] = str(self.name)
        obj['position'] = self.position.toJSON()
        if not self.direction.isUp:
            obj['direction'] = self.direction
        connections = self.connectionsToJSON()
        if connections != {}:
            obj['connections'] = connections

        if self.control_behavior is not None:
            obj['control_behavior'] = self.control_behavior
        if self.items is not None:
            obj['items'] = self.items
        if self.recipe != 'None':
            obj['recipe'] = self.recipe
        if self.bar is not None:
            obj['bar'] = self.bar
        if self.infinity_settings is not None:
            obj['infinity_settings'] = self.infinity_settings
        if self.type is not None:
            obj['type'] = self.type
        if self.input_priority is not None:
            obj['input_priority'] = self.input_priority
        if self.output_priority is not None:
            obj['output_priority'] = self.output_priority
        if self.filter is not None:
            obj['filter'] = self.filter
        if self.filters is not None:
            obj['filters'] = self.filters
        if self.override_stack_size is not None:
            obj['override_stack_size'] = self.override_stack_size
        if self.drop_position is not None:
            obj['drop_position'] = self.drop_position.toJSON()
        if self.pickup_position is not None:
            obj['pickup_position'] = self.pickup_position.toJSON()
        if self.request_filters is not None:
            obj['request_filters'] = self.request_filters
        if self.request_from_buffers is not None:
            obj['request_from_buffers'] = self.request_from_buffers
        if self.parameters is not None:
            obj['parameters'] = self.parameters
        if self.alert_parameters is not None:
            obj['alert_parameters'] = self.alert_parameters
        if self.auto_launch is not None:
            obj['auto_launch'] = self.auto_launch
        if self.variation is not None:
            obj['variation'] = self.variation
        if self.color is not None:
            obj['color'] = self.color.toJSON()
        if self.station is not None:
            obj['station'] = self.station

        return obj

