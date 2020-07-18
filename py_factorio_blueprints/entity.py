from py_factorio_blueprints.util import \
    Vector, NameStr, Connection, Direction, ControlBehaviorMeta
from py_factorio_blueprints.entity_mixins import \
    BaseMixin, SignalName, Base
from py_factorio_blueprints.exceptions import *


class PositionField:
    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        setattr(instance, self.name, Vector(value))

    def __get__(self, instance, owner):
        return getattr(instance, self.name, Vector(0, 0))


class DirectionField:
    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        setattr(instance, self.name, Direction(value))

    def __get__(self, instance, owner):
        return getattr(instance, self.name, Direction(0))


class ItemName(Base):
    class NameStr(str):
        @property
        def data(self):
            from py_factorio_blueprints import Blueprint
            return Blueprint.entity_prototypes[self]

    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        if not getattr(instance, 'strict', True):
            setattr(instance, self.name, value)
            return

        from py_factorio_blueprints import Blueprint

        if value not in Blueprint.item_prototypes:
            raise UnknownItem
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return ItemName.NameStr(getattr(instance, self.name, ""))


class EntityName(Base):
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

    def __set_name__(self, owner, name):
        self.name = name
        self._name = "__" + name

    def __set__(self, instance, value):
        if not getattr(instance, 'strict', True):
            setattr(instance, self._name, value)
            return

        from py_factorio_blueprints.blueprint import Blueprint

        if value not in Blueprint.entity_prototypes:
            raise UnknownEntity(value)
        setattr(instance, self._name, value)
        prototype = Blueprint.entity_prototypes[value]['type']

        if instance.blueprint:
            custom_prototypes = instance.blueprint.custom_entity_prototypes\
                .get(prototype, {})
            custom_mixins = custom_prototypes.get('mixins', [])
        else:
            custom_mixins = []
        from py_factorio_blueprints.entity_prototypes import entity_prototypes
        mixins = entity_prototypes[prototype].get('mixins', [])
        instance.add_mixins(*custom_mixins, *mixins)

    def __get__(self, instance, owner):
        return EntityName.NameStr(getattr(instance, self._name, ""))


class Entity(BaseMixin):
    ID = 'entity_number'
    name = EntityName()
    position = PositionField()
    direction = DirectionField()

    def __repr__(self):
        return f'<Entity (name: "{self.name}", position: ' \
               f'{self.position}, direction: {self.direction})>'

    def __str__(self):
        return f'<Entity (name: "{self.name}")>'

    def set_mixins(self, *mixins):
        """ Resets self to the base Entity class and adds the given mixins """
        self.__class__ = type('Entity', (Entity, *mixins), {})

    def add_mixins(self, *mixins):
        """ Adds additional mixins to the current self class """
        self.__class__ = type('Entity', (self.__class__, *mixins), {})

    def __init__(self, *args, name, position, strict=True,
                 blueprint_layer=None,
                 direction=0, entity_number=None, **kwargs):
        self.strict = strict
        self._blueprint_layer = blueprint_layer
        self.entity_number = entity_number
        self._auto_entity_number = entity_number
        self.name = name
        self.position = position
        self.direction = direction

        self.raw_connections = kwargs.pop('connections', None)
        # self.connections = []

        if 'control_behavior' in kwargs:
            self.control_behavior = self.ControlBehavior(
                _entity=self,
                **kwargs.pop('control_behavior'))

        super().__init__(*args, **kwargs)

    @property
    def blueprint(self):
        try:
            return self._blueprint_layer.blueprint
        except AttributeError:
            return None

    def get_connections(self):
        connections = [connection.orientate(self)
                       for connection in self.blueprint.connections
                       if connection.attached_to(self)]
        return sorted(
            connections, key=lambda x: (
                x.from_entity._auto_entity_number,
                x.to_entity._auto_entity_number))

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
            if connection.to_entity is self:
                if connection.to_side not in obj:
                    obj[connection.to_side] = {}
                if connection.color not in obj[connection.to_side]:
                    obj[connection.to_side][connection.color] = []
                result = {
                    'entity_id': self._auto_entity_number
                }
                if self.NR_CONNECTIONS == 2:
                    result['circuit_id'] = connection.from_side
                obj[connection.to_side][connection.color].append(result)

            result = {
                'entity_id': connection.to_entity._auto_entity_number,
            }
            if connection.to_entity.NR_CONNECTIONS == 2:
                result['circuit_id'] = connection.from_side
            obj[connection.from_side][connection.color].append(result)
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

    @property
    def selection_box(self):
        selection_box = self.name.selection_box
        def r(box):
            top_left, bottom_right = box
            return top_left.yx, bottom_right.yx

        for _ in range(self.direction // 2):
            selection_box = r(selection_box)

        return selection_box

    def collides(self, position):
        top_left, bottom_right = self.selection_box
        position -= self.position
        return top_left < position < bottom_right

    def rotate(self, amount,
               around=Vector(0, 0), direction=Direction.CLOCKWISE):
        position = self.position - around
        amount %= 4
        if direction != Direction.CLOCKWISE:
            amount %= 4 - amount

        def r(v):
            return Vector(-v.y, v.x)

        for _ in range(amount):
            position = r(position)
        self.position = position + around

        mixin = super()
        if hasattr(mixin, "rotate"):
            mixin.rotate(amount)

    def to_json(self, obj=None):
        if obj is None:
            obj = {}
        obj['entity_number'] = self._auto_entity_number
        obj['name'] = self.name
        obj['position'] = self.position.to_json()
        connections = self.connections_to_json()
        if connections != {}:
            obj['connections'] = connections
        return super().to_json(obj)
