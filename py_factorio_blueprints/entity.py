from py_factorio_blueprints.util import Vector, namestr, Color, Connection


class Direction(int):
    def __init__(self, direction=0):
        self._dir = int(direction)

    def __set__(self, instance, value):
        self._dir = value % 8

    def __get__(self, instance, owner):
        return self._dir

    def __repr__(self):
        return str(self._dir)

    def __str__(self):
        return str(self._dir)

    @property
    def isUp(self):
        return self._dir == 0

    @property
    def isRight(self):
        return self._dir == 2

    @property
    def isDown(self):
        return self._dir == 4

    @property
    def isLeft(self):
        return self._dir == 6

    def rotate(self, amount, direction='clockwise'):
        amount *= 2
        if direction != 'clockwise':
            amount = -amount
        self._dir = (self._dir + amount) % 8


class Entity():
    def __init__(self, blueprint, data):
        self.blueprint = blueprint
        self.entity_number = data['entity_number']
        self.name = namestr(data['name'])
        self.position = Vector(data['position']['x'], data['position']['y'])
        self.direction = Direction(data.get('direction', 0))

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

        self.override_stack_size = data.get('override_stack_size', None)

        drop_position = data.get('drop_position', None)
        if drop_position:
            self.drop_position = Vector(drop_position['x'], drop_position['y'])
        else:
            self.drop_position = None
        pickup_position = data.get('pickup_position', None)
        if pickup_position:
            self.pickup_position = Vector(pickup_position['x'], pickup_position['y'])
        else:
            self.pickup_position = None

        self.request_filters = data.get('request_filters', None)
        self.request_from_buffers = data.get('request_from_buffers', None)

        self.parameters = data.get('parameters', None)
        self.alert_parameters = data.get('alert_parameters', None)

        self.auto_launch = data.get('auto_launch', None)

        self.variation = data.get('variation', None)
        color = data.get('color', None)
        if color is not None:
            self.color = Color(color)
        else:
            self.color = None
        self.station = data.get('station', None)

    def getConnections(self):
        connections = [connection.orientate(self) for connection in self.blueprint.connections if connection.attachedTo(self)]
        return connections

    def connect(self, to_entity, from_side='in', to_side='in', color='red'):
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
        offset = Vector((width - 1) / 2.0, -(height - 1) / 2.0)
        self.position
        topleft = self.position - offset
        for y in range(int(topleft.y), int(topleft.y) - height, -1):
            for x in range(int(topleft.x), int(topleft.x) + width):
                yield (x, y)

    def place(self):
        for x, y in self.coordinates:
            self.blueprint[(x, y)] = self

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
        self.direction.rotate(amount)

    def toJSON(self):
        obj = {}
        obj['entity_number'] = self.entity_number
        obj['name'] = str(self.name)
        obj['position'] = self.position.toJSON()
        if not self.direction.isUp:
            obj['direction'] = str(self.direction)
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


