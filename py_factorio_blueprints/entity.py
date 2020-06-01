from py_factorio_blueprints.util import \
    Vector, NameStr, Connection, Direction
from py_factorio_blueprints.entity_mixins import BaseMixin
from py_factorio_blueprints.exceptions import *


class CombinatorControl:
    def __init__(self, first, operator, second, output, type="arithmetic"):
        self.type = type
        self.operator = operator
        self.first = first
        self.second = second
        self.output = output

    @classmethod
    def from_entity_data(cls, data):
        combinator_type = data["name"][0:-11]
        control_behavior = data.get("control_behavior", None)
        if control_behavior is None:
            return None
        condition_data = control_behavior.get(
            "{}_conditions".format(combinator_type), None)
        if condition_data is None:
            return None
        operator = condition_data["operation"]\
            if combinator_type == "arithmetic" \
            else condition_data["comparator"]

        def get_from(d, key):
            value = d.get("{}_constant".format(key), None)
            if value is None:
                value = d.get("{}_signal".format(key))["name"]
            return value

        first = get_from(condition_data, "first")
        second = get_from(condition_data, "second")
        output = get_from(condition_data, "output")

        return cls(first, operator, second, output, type=combinator_type)

    @property
    def first(self):
        return self.__first

    @first.setter
    def first(self, value):
        if isinstance(value, int):
            self.__first = value
        else:
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
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = NameStr(value)

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
            operators = ["*", "/", "+", "-", "%", "^",
                         "<<", ">>", "AND", "OR", "XOR"]
        else:
            operators = [">", "<", "=", ">=", "<=", "!="]
        if value not in operators:
            raise ValueError("{} not in {}".format(value, operators))
        self.__operator = value

    def to_json(self):
        control_behavior = {}
        for slot in ["first", "second"]:
            if isinstance(getattr(self, slot), int):
                control_behavior[
                    "{}_constant".format(slot)
                ] = getattr(self, slot)
            else:
                control_behavior["{}_signal".format(slot)] = {
                    "type": getattr(self, slot).metadata["type"],
                    "name": getattr(self, slot)
                }
        control_behavior["output_signal"] = {
            "type": self.output.metadata["type"],
            "name": self.output
        }
        control_behavior["operation"
                         if self.type == "arithmetic"
                         else "comparator"] = self.operator
        result = {
            "{}_conditions".format(self.type): control_behavior
        }
        return result


class PositionField:
    def __set__(self, instance, value):
        instance.__position = Vector(value)

    def __get__(self, instance, owner):
        try:
            return instance.__position
        except AttributeError:
            return None


class DirectionField:
    def __set__(self, instance, value):
        instance.__direction = Direction(value)

    def __get__(self, instance, owner):
        try:
            return instance.__direction
        except AttributeError:
            return Direction(0)


class EntityName:
    class NameStr(str):
        @property
        def prototype(self):
            return self.data['type']

        @property
        def data(self):
            from py_factorio_blueprints.blueprint import Blueprint
            return Blueprint.entity_prototypes[self]

        @property
        def selection_box(self):
            return (
                Vector(**self.data['selection_box']['left_top']),
                Vector(**self.data['selection_box']['right_bottom'])
            )

    def __init__(self, strict=True):
        self.strict = strict

    def __set__(self, instance, value):
        if not self.strict:
            instance.__name = value
            return

        from py_factorio_blueprints.blueprint import Blueprint

        if value not in Blueprint.entity_prototypes:
            raise UnknownEntity(value)
        instance.__name = value

    def __get__(self, instance, owner):
        return EntityName.NameStr(instance.__name)


class RecipeName:
    class NameStr(str):
        @property
        def data(self):
            from py_factorio_blueprints.blueprint import Blueprint
            return Blueprint.recipe_prototypes[self]

    def __init__(self, strict=True):
        self.strict = strict

    def __set__(self, instance, value):
        if not self.strict:
            instance.__name = value
            return

        from py_factorio_blueprints.blueprint import Blueprint

        if value not in Blueprint.recipe_prototypes:
            raise UnknownRecipe(value)
        instance.__name = value

    def __get__(self, instance, owner):
        return RecipeName.NameStr(instance.__name)


class Entity(BaseMixin):
    name = EntityName()
    position = PositionField()
    direction = DirectionField()

    def __repr__(self):
        return '<Entity (name: "{name}", position: ' \
               '{pos}, direction: {dir})>'.format(
                    name=self.name,
                    pos=self.position,
                    dir=self.direction)

    def __str__(self):
        return '<Entity (name: "{name}")>'.format(
            name=self.name)

    @classmethod
    def create_entity(cls, name, position, direction,
                      *args, **kwargs):
        data = {
            "name": name,
            "position": position,
            "direction": direction
        }
        return cls(data, *args, **kwargs)

    def __init__(self, *args, name, position,
                 direction=0, entity_number=None, **kwargs):
        self.blueprint = None
        self.entity_number = entity_number
        self.name = name
        self.position = position
        self.direction = direction

        self.selection_box = self.name.selection_box

        if self.direction.is_left or self.direction.is_right:
            self.__rotate_selection_box()

        self.raw_connections = kwargs.pop('connections', None)
        # self.connections = []

        super().__init__(*args, **kwargs)

    @property
    def blueprint(self):
        return self.__blueprint

    @blueprint.setter
    def blueprint(self, value):
        self.__blueprint = value

    def get_connections(self):
        connections = [connection.orientate(self)
                       for connection in self.blueprint.connections
                       if connection.attached_to(self)]
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

    def connections_to_json(self):
        connections = self.get_connections()
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
    def top_left(self):
        top_left, bottom_right = self.selection_box
        return self.position + top_left

    @property
    def top_right(self):
        top_left, bottom_right = self.selection_box
        return self.position + Vector(bottom_right.x, top_left.y)

    @property
    def bottom_left(self):
        top_left, bottom_right = self.selection_box
        return self.position + Vector(top_left.x, bottom_right.y)

    @property
    def bottom_right(self):
        top_left, bottom_right = self.selection_box
        return self.position + bottom_right

    def __rotate_selection_box(self):
        top_left, bottom_right = self.selection_box
        self.selection_box = (top_left.yx, bottom_right.yx)

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
            self.__rotate_selection_box()
        self.position = position + around

        mixin = super()
        if hasattr(mixin, "rotate"):
            mixin.rotate(amount)

    def to_json(self, obj=None):
        if obj is None:
            obj = {}
        obj['entity_number'] = self.entity_number,
        obj['name'] = str(self.name),
        obj['position'] = self.position.to_json()
        connections = self.connections_to_json()
        if connections != {}:
            obj['connections'] = connections
        return super().to_json(obj)
