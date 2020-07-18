from py_factorio_blueprints.util import (
    NameStr, Vector, Color as ColorObj, Condition, obj_set, ControlBehaviorMeta)
from py_factorio_blueprints.exceptions import *


class Base(metaclass=ControlBehaviorMeta):
    pass


class BaseMixin(Base):
    NR_CONNECTIONS = 1
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.__entity = kwargs.pop('_entity')
            if not self.__entity:
                raise TypeError("Entity can't be NoneType")
            if args:
                raise TypeError(
                    f"{self.__class__}.__init__() "
                    f"({self.__entity.name}({self.__entity.name.data['type']})) "
                    f"takes no arguments. "
                    f"arguments provided: {args}")
            if kwargs:
                raise TypeError(
                    f"{self.__class__}.__init__() "
                    f"({self.__entity.name}({self.__entity.name.data['type']})) "
                    f"takes no keyword arguments. "
                    f"keyword arguments provided: {kwargs}")

        def to_json(self, obj):
            if not obj:
                return None
            return obj

    def __init__(self, *args, **kwargs):
        if args:
            raise TypeError(
                f"{self.__class__}.__init__() "
                f"({self.name}({self.name.data['type']})) "
                f"takes no arguments. "
                f"arguments provided: {args}")
        if kwargs:
            raise TypeError(
                f"{self.__class__}.__init__() "
                f"({self.name}({self.name.data['type']})) "
                f"takes no keyword arguments. "
                f"keyword arguments provided: {kwargs}")

    def to_json(self, obj):
        if hasattr(self, 'control_behavior'):
            obj_set(obj, 'control_behavior', self.control_behavior.to_json({}))
        return obj


class Operator(Base):
    def __init__(self, options):
        self.__options = options

    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        if value not in [*self.__options, None]:
        # if value not in [">", "<", "=", "≥", "≤", "!=", None]:
            raise ValueError(value)
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)


class SignalName(Base):
    class NameStr(str):
        @property
        def data(self):
            from py_factorio_blueprints.blueprint import Blueprint
            return Blueprint.signal_prototypes[self]

        def to_json(self):
            return {
                'name': self,
                'type': self.data['type']
            }

    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        if not getattr(instance, 'strict', True):
            setattr(instance, self.name, value)
            return

        if type(value) is int:
            setattr(instance, self.name, value)
            return
        if type(value) is dict:
            value = value.get('name', None)

        from py_factorio_blueprints.blueprint import Blueprint

        if value and value not in Blueprint.signal_prototypes:
            raise UnknownSignal(value)
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        value = getattr(instance, self.name, None)
        if value is None:
            return None
        if type(value) is int:
            return value
        return SignalName.NameStr(value)


class Accumulator(BaseMixin):
    class ControlBehavior:
        output_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.output_signal = kwargs.pop(
                'output_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'output_signal', self.output_signal)
            return super().to_json(obj)


class Items(BaseMixin):
    class Item(Base):
        name = SignalName()

        def __init__(self, *, name, count):
            self.name = name
            self.count = count

    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items', {})
        self.items = [
            self.Item(name=item, count=count)
            for item, count in items.items()]
        super().__init__(*args, *kwargs)

    def to_json(self, obj):
        if self.items:
            obj['items'] = {
                item.name: item.count
                for item in self.items}

        return super().to_json(obj)


class Filters(BaseMixin):
    class Filter(Base):
        signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.signal = kwargs.pop(
                'signal', None)
            self.count = kwargs.pop(
                'count', None)
            self.index = kwargs.pop(
                'index', None)
            super().__init__(*args, *kwargs)

        def to_json(self):
            return {
                'signal': self.signal.to_json(),
                'count': self.count,
                'index': self.index
            }

    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            entity = kwargs.get('_entity')
            filters = kwargs.pop('filters', [])
            self.filters = [
                entity.Filter(**filter)
                for filter in filters]
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            if self.filters:
                obj['filters'] = [
                    filter.to_json()
                    for filter in self.filters]
            return super().to_json(obj)


class ConstantCombinator(Filters):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.is_on = kwargs.pop('is_on', True)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            if not self.is_on:
                obj['is_on'] = False
            return super().to_json(obj)


class Combinator(BaseMixin):
    NR_CONNECTIONS = 2
    TYPE = ''
    OPERATOR = ''

    class ControlBehavior:
        first = SignalName()
        second = SignalName()
        output = SignalName()

        def __init__(self, *args, **kwargs):
            _entity = kwargs.get('_entity')
            self.__field = f"{_entity.TYPE}_conditions"
            conditions = kwargs.pop(self.__field, {})
            self.operator = conditions.pop(_entity.OPERATOR)

            def get_from(d, key):
                if _entity.TYPE == 'decider' and key == 'first':
                    value = d.pop("constant", None)
                else:
                    value = d.pop(f"{key}_constant", None)
                if value is None:
                    value = d.pop(f"{key}_signal", None)
                    if value is None:
                        return None
                    return value["name"]
                return value

            self.first = get_from(conditions, "first")
            self.second = get_from(conditions, "second")
            self.output = get_from(conditions, "output")
            if conditions:
                kwargs[self.__field] = conditions
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            def set_to(combinator, key, value):
                if type(value) is int:
                    if combinator == 'decider_conditions':
                        return "constant", value
                    else:
                        return f"{key}_constant", value
                else:
                    return f"{key}_signal", value
            fields = ['first', 'second', 'output']
            combinator_settings = {}
            combinator_settings[self.__entity.OPERATOR] = self.operator
            for field in fields:
                key, value = set_to(self.__field, field, getattr(self, field))
                obj_set(combinator_settings, key, value)
            if combinator_settings:
                if self.__field not in obj:
                    obj[self.__field] = {}
                obj[self.__field] = {**combinator_settings, **obj[self.__field]}
            return super().to_json(obj)


class Arithmetic(Combinator):
    TYPE = 'arithmetic'
    OPERATOR = 'operation'

    class ControlBehavior:
        operator = Operator(
            ['*', '/', '+', '-', '%', '^', '<<', '>>', 'AND', 'OR', 'XOR'])


class Decider(Combinator):
    TYPE = 'decider'
    OPERATOR = 'comparator'

    class ControlBehavior:
        operator = Operator([">", "<", "=", "≥", "≤", "!="])
        def __init__(self, *args, **kwargs):
            _entity = kwargs.get('_entity')
            self.__field = f"{_entity.TYPE}_conditions"
            conditions = kwargs.pop(self.__field)
            self.copy_count_from_input = conditions.pop(
                'copy_count_from_input', False)
            if conditions:
                kwargs[self.__field] = conditions
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            if not obj.get(self.__field, None):
                obj[self.__field] = {}
            obj[self.__field]['copy_count_from_input'] =\
                self.copy_count_from_input
            return super().to_json(obj)


class TransportBelt(BaseMixin):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.circuit_enable_disable = kwargs.pop(
                'circuit_enable_disable', None)
            self.circuit_read_hand_contents = kwargs.pop(
                'circuit_read_hand_contents', None)
            self.circuit_contents_read_mode = kwargs.pop(
                'circuit_contents_read_mode', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj['circuit_read_hand_contents'] = self.circuit_read_hand_contents
            obj['circuit_enable_disable'] = self.circuit_enable_disable
            obj['circuit_contents_read_mode'] = self.circuit_contents_read_mode
            return super().to_json(obj)


class TrainSignal(BaseMixin):
    class ControlBehavior:
        red_output_signal = SignalName()
        orange_output_signal = SignalName()
        green_output_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.circuit_read_signal = kwargs.pop(
                'circuit_read_signal', None)
            self.red_output_signal = kwargs.pop(
                'red_output_signal', None)
            self.orange_output_signal = kwargs.pop(
                'orange_output_signal', None)
            self.green_output_signal = kwargs.pop(
                'green_output_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'circuit_read_signal', self.circuit_read_signal)
            obj_set(obj, 'red_output_signal', self.red_output_signal)
            obj_set(obj, 'orange_output_signal', self.orange_output_signal)
            obj_set(obj, 'green_output_signal', self.green_output_signal)
            return super().to_json(obj)


class ChainSignal(TrainSignal):
    class ControlBehavior:
        blue_output_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.blue_output_signal = kwargs.pop(
                'blue_output_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'blue_output_signal', self.blue_output_signal)
            return super().to_json(obj)


class RailSignal(TrainSignal):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.circuit_close_signal = kwargs.pop(
                'circuit_close_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'circuit_close_signal', self.circuit_close_signal)
            return super().to_json(obj)


class Orientation(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate(self, amount, **kwargs):
        self.orientation = self.orientation + (0.25 * amount) % 1
        sup = super()
        if hasattr(sup, 'rotate'):
            sup.rotate(amount, **kwargs)


class Train(Orientation):
    def __init__(self, *args, orientation=None, **kwargs):
        self.orientation = orientation
        super().__init__(*args, **kwargs)

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        if value is None:
            self.__orientation = None
        else:
            self.__orientation = value % 1.0

    def to_json(self, obj):
        obj_set(obj, 'orientation', self.orientation)
        return super().to_json(obj)


class Cargo(Train):
    def __init__(self, *args, inventory=None, **kwargs):
        self.inventory = inventory
        super().__init__(*args, **kwargs)

    @property
    def inventory_filters(self):
        return self.__inventory_filters

    @property
    def inventory_bar(self):
        return self.__inventory_bar

    @inventory_bar.setter
    def inventory_bar(self, value):
        if value is None:
            self.__inventory_bar = None
        else:
            self.__inventory_bar = int(value)

    @property
    def inventory(self):
        if self.__inventory_bar is None and not len(self.__inventory_filters):
            return None
        inventory = {}
        obj_set(inventory, 'bar', self.__inventory_bar)
        if len(self.__inventory_filters):
            inventory["filters"] = [
                {"index": index, "name": name}
                for index, name in self.__inventory_filters.items()]
        return inventory

    @inventory.setter
    def inventory(self, value):
        self.__inventory_filters = []
        if value is None:
            self.__inventory_bar = None
            return
        self.__inventory_bar = value.get("bar", None)
        self.__inventory_filters = {}
        for f in value.get("filters", []):
            self.__inventory_filters[f["index"]] = NameStr(f["name"])

    def to_json(self, obj):
        obj_set(obj, 'inventory', self.inventory)
        return super().to_json(obj)


class ColorField(Base):
    def __set_name__(self, owner, name):
        self.__name = f"__{name}"

    def __set__(self, instance, value):
        if value is None:
            setattr(instance, self.__name, None)
        else:
            setattr(instance, self.__name, ColorObj(**value))

    def __get__(self, instance, owner):
        return getattr(instance, self.__name, None)

class Color(BaseMixin):
    color = ColorField()

    def __init__(self, *args, **kwargs):
        self.color = kwargs.pop('color', None)
        super().__init__(*args, **kwargs)

    def to_json(self, obj):
        obj_set(obj, 'color', self.color)
        return super().to_json(obj)


class Container(BaseMixin):
    def __init__(self, *args, bar=None, **kwargs):
        self.bar = bar
        super().__init__(*args, **kwargs)

    @property
    def bar(self):
        return self.__bar

    @bar.setter
    def bar(self, value):
        if value is None:
            self.__bar = None
        else:
            self.__bar = int(value)

    def to_json(self, obj):
        obj_set(obj, 'bar', self.bar)
        return super().to_json(obj)


class CircuitCondition(BaseMixin):
    class ControlBehavior:
        first = SignalName()
        comparator = Operator([">", "<", "=", "≥", "≤", "!="])
        second = SignalName()

        def __init__(self, *args,  circuit_condition=None, **kwargs):
            if circuit_condition is None:
                circuit_condition = {}
            else:
                self.first = circuit_condition.get(
                    'first_signal', None)
                self.second = circuit_condition.get(
                    'second_signal',
                    circuit_condition.get('constant', None))
                self.comparator = circuit_condition.get('comparator', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            circuit_condition = {}
            obj_set(circuit_condition, 'comparator', self.comparator)
            if self.first is not None:
                if type(self.first) is int:
                    circuit_condition['first_constant'] = self.first
                else:
                    circuit_condition['first_signal'] = self.first.to_json()
            if self.second is not None:
                if type(self.second) is int:
                    circuit_condition['constant'] = self.second
                else:
                    circuit_condition['second_signal'] = self.second.to_json()
            if circuit_condition:
                obj['circuit_condition'] = circuit_condition
            return super().to_json(obj)


class Lamp(CircuitCondition):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.use_colors = kwargs.pop(
                'use_colors', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'use_colors', self.use_colors)
            return super().to_json(obj)


class MiningDrill(CircuitCondition):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.circuit_enable_disable = kwargs.pop(
                'circuit_enable_disable', True)
            self.circuit_read_resources = kwargs.pop(
                'circuit_read_resources', True)
            self.circuit_resource_read_mode = kwargs.pop(
                'circuit_resource_read_mode', 0)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj['circuit_enable_disable'] = self.circuit_enable_disable
            obj['circuit_read_resources'] = self.circuit_read_resources
            obj['circuit_resource_read_mode'] = self.circuit_resource_read_mode
            return super().to_json(obj)


class Inserter(BaseMixin):
    class ControlBehavior:
        stack_control_input_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.circuit_mode_of_operation = kwargs.pop(
                'circuit_mode_of_operation', None)
            self.circuit_set_stack_size = kwargs.pop(
                'circuit_set_stack_size', None)
            self.stack_control_input_signal = kwargs.pop(
                'stack_control_input_signal', None)
            self.circuit_hand_read_mode = kwargs.pop(
                'circuit_hand_read_mode', None)
            self.circuit_read_hand_contents = kwargs.pop(
                'circuit_read_hand_contents', None)

        def to_json(self, obj):
            obj_set(obj, 'circuit_mode_of_operation',
                    self.circuit_mode_of_operation)
            obj_set(obj, 'circuit_set_stack_size', self.circuit_set_stack_size)
            obj_set(obj, 'stack_control_input_signal',
                    self.stack_control_input_signal)
            obj_set(obj, 'circuit_hand_read_mode', self.circuit_hand_read_mode)
            obj_set(obj, 'circuit_read_hand_contents',
                    self.circuit_read_hand_contents)

            return super().to_json(obj)

    def __init__(self, *args, override_stack_size=None, drop_position=None,
                 pickup_position=None, **kwargs):
        self.override_stack_size = override_stack_size
        self.pickup_position = pickup_position
        self.drop_position = drop_position
        super().__init__(*args, **kwargs)

    @property
    def pickup_position(self):
        return self.__pickup_position

    @pickup_position.setter
    def pickup_position(self, value):
        self.__pickup_position = Vector(value)

    @property
    def drop_position(self):
        return self.__drop_position

    @drop_position.setter
    def drop_position(self, value):
        self.__drop_position = Vector(value)

    @property
    def override_stack_size(self):
        return self.__override_stack_size

    @override_stack_size.setter
    def override_stack_size(self, value):
        if value is not None:
            value = int(value)
        self.__override_stack_size = value

    def to_json(self, obj):
        obj_set(obj, 'override_stack_size', self.override_stack_size)
        obj_set(obj, 'pickup_position', self.pickup_position)
        obj_set(obj, 'drop_position', self.drop_position)
        return super().to_json(obj)


class FilterInserter(Inserter):
    class Filter(Base):
        name = SignalName()

        def __init__(self, *args, **kwargs):
            self.name = kwargs.pop(
                'name', None)
            self.index = kwargs.pop(
                'index', None)
            super().__init__(*args, *kwargs)

        def to_json(self):
            return {'index': self.index, 'name': self.name}

    def __init__(self, *args, filters=None, filter_mode=None, **kwargs):
        if filters is None:
            filters = []
        self.filters = [
            self.Filter(**filter)
            for filter in filters]
        self.filter_mode = filter_mode
        super().__init__(*args, **kwargs)

    @property
    def filter_mode(self):
        return self.__filter_mode

    @filter_mode.setter
    def filter_mode(self, value):
        if value not in [None, "whitelist", "blacklist"]:
            raise ValueError(value)
        self.__filter_mode = value

    def to_json(self, obj):
        obj_set(obj, "filter_mode", self.filter_mode)
        if self.filters:
            obj["filters"] = [
                filter.to_json()
                for filter in self.filters]
        return super().to_json(obj)


class InfinityContainer(BaseMixin):
    def __init__(self, *args, infinity_settings=None, **kwargs):
        self.infinity_settings = infinity_settings
        super().__init__(*args, **kwargs)

    @property
    def infinity_settings(self):
        return {
            "remove_unfiltered_items":
                self.infinity_settings_remove_unfiltered_items,
            "filters": self.infinity_settings_filters
        }

    @infinity_settings.setter
    def infinity_settings(self, value):
        self.infinity_settings_remove_unfiltered_items =\
            value["remove_unfiltered_items"]
        self.infinity_settings_filters = value["filters"]

    @property
    def infinity_settings_remove_unfiltered_items(self):
        return self.__infinity_settings_remove_unfiltered_items

    @infinity_settings_remove_unfiltered_items.setter
    def infinity_settings_remove_unfiltered_items(self, value):
        self.__infinity_settings_remove_unfiltered_items = bool(value)

    @property
    def infinity_settings_filters(self):
        return self.__infinity_settings_filters

    @infinity_settings_filters.setter
    def infinity_settings_filters(self, values):
        self.__infinity_settings_filters = {}
        if values is None:
            values = []
        for value in values:
            if value["mode"] not in ["at-least", "at-most", "exactly"]:
                raise ValueError(value["mode"])
            self.__infinity_settings_filters[value["index"]] = {
                "count": value["count"],
                "mode": value["mode"],
                "name": NameStr(value["name"])
            }

    def to_json(self, obj):
        if self.infinity_settings:
            obj["infinity_settings"] = {
                "remove_unfiltered_items":
                    self.infinity_settings_remove_unfiltered_items,
                "filters": [
                    {
                        "index": index,
                        "count": value["count"],
                        "mode": value["mode"],
                        "name": value["name"]
                    }
                    for index, value in
                    self.infinity_settings_filters.items()
                ]
            }
        return super().to_json(obj)


class RecipeName(Base):
    class NameStr(str):
        @property
        def data(self):
            from py_factorio_blueprints.blueprint import Blueprint
            return Blueprint.recipe_prototypes[self]

    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        if not getattr(instance, 'strict', True):
            setattr(instance, self.name, value)
            return

        from py_factorio_blueprints.blueprint import Blueprint

        if value is not None and value not in Blueprint.recipe_prototypes:
            raise UnknownRecipe(value)
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        value = getattr(instance, self.name, None)
        if value is None:
            return None
        return RecipeName.NameStr(value)


class Recipe(BaseMixin):
    recipe = RecipeName()

    def __init__(self, *args, recipe=None, **kwargs):
        self.recipe = recipe
        super().__init__(*args, **kwargs)

    def to_json(self, obj):
        obj_set(obj, 'recipe', self.recipe)
        return super().to_json(obj)


class Requester(BaseMixin):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            self.circuit_mode_of_operation = kwargs.pop(
                'circuit_mode_of_operation', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'circuit_mode_of_operation',
                    self.circuit_mode_of_operation)
            return super().to_json(obj)

    def __init__(self, *args,
                 request_from_buffers=False, request_filters=None, **kwargs):
        self.request_from_buffers = request_from_buffers
        self.request_filters = request_filters
        super().__init__(*args, **kwargs)

    @property
    def request_from_buffers(self):
        return self.__request_from_buffers

    @request_from_buffers.setter
    def request_from_buffers(self, value):
        self.__request_from_buffers = value

    @property
    def request_filters(self):
        return self.__request_filters

    @request_filters.setter
    def request_filters(self, values):
        if values is None:
            values = []
        self.__request_filters = {}
        for value in values:
            self.__request_filters[value["index"]] = {
                "name": NameStr(value["name"]),
                "count": int(value["count"])
            }

    def to_json(self, obj):
        if self.request_from_buffers:
            obj["request_from_buffers"] = self.request_from_buffers
        if self.request_filters:
            obj["request_filters"] = [
                {
                    "index": index,
                    "name": f["name"],
                    "count": f["count"]
                }
                for index, f in self.request_filters.items()
            ]
        return super().to_json(obj)


class Roboport(BaseMixin):
    class ControlBehavior:
        available_logistic_output_signal = SignalName()
        total_logistic_output_signal = SignalName()
        available_construction_output_signal = SignalName()
        total_construction_output_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.read_logistics = kwargs.pop(
                'read_logistics', None)
            self.read_robot_stats = kwargs.pop(
                'read_robot_stats', None)
            self.available_construction_output_signal = kwargs.pop(
                'available_construction_output_signal', None)
            self.total_construction_output_signal = kwargs.pop(
                'total_construction_output_signal', None)
            self.available_logistic_output_signal = kwargs.pop(
                'available_logistic_output_signal', None)
            self.total_logistic_output_signal = kwargs.pop(
                'total_logistic_output_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'read_logistics', self.read_logistics)
            obj_set(obj, 'read_robot_stats', self.read_robot_stats)
            fields = [
                'available_construction_output_signal',
                'total_construction_output_signal',
                'available_logistic_output_signal',
                'total_logistic_output_signal'
            ]
            for field in fields:
                if getattr(self, field):
                    obj[field] = getattr(self, field).to_json()
            return super().to_json(obj)


class Rotatable(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate(self, amount, **kwargs):
        self.direction = self.direction.rotate(amount)
        sup = super()
        if hasattr(sup, "rotate"):
            sup.rotate(amount, **kwargs)

    def to_json(self, obj):
        if not self.direction.is_up:
            obj['direction'] = self.direction
        return super().to_json(obj)


class Silo(BaseMixin):
    def __init__(self, *args, auto_launch=None, **kwargs):
        self.auto_launch = auto_launch
        super().__init__(*args, **kwargs)

    @property
    def auto_launch(self):
        return self.__auto_launch

    @auto_launch.setter
    def auto_launch(self, value):
        if value not in [None, True, False]:
            raise ValueError
        self.__auto_launch = value

    def to_json(self, obj):
        obj_set(obj, 'auto_launch', self.auto_launch)
        return super().to_json(obj)


class Speaker(CircuitCondition):
    class ControlBehavior:
        def __init__(self, *args, **kwargs):
            entity = kwargs.get('_entity')
            self.circuit_parameters = entity.CircuitParameters(
                **kwargs.pop('circuit_parameters', {}))
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj['circuit_parameters'] = self.circuit_parameters.to_json()
            return super().to_json(obj)

    class CircuitParameters:
        def __init__(self, *args, **kwargs):
            self.signal_value_is_pitch = kwargs.pop(
                'signal_value_is_pitch', None)
            self.instrument_id = kwargs.pop(
                'instrument_id', None)
            self.note_id = kwargs.pop(
                'note_id', None)
            super().__init__(*args, **kwargs)

        def to_json(self):
            return {
                'instrument_id': self.instrument_id,
                'note_id': self.note_id,
                'signal_value_is_pitch': self.signal_value_is_pitch}

    def __init__(self, *args, parameters=None, alert_parameters=None, **kwargs):
        self.parameters = parameters
        self.alert_parameters = alert_parameters
        super().__init__(*args, **kwargs)

    @property
    def parameters(self):
        return self.__parameters

    @parameters.setter
    def parameters(self, value):
        if value is None:
            self.__parameters = None
            return
        self.__parameters = {
            "playback_volume": float(value["playback_volume"]),
            "playback_globally": bool(value["playback_globally"]),
            "allow_polyphony": bool(value["allow_polyphony"])
        }

    @property
    def alert_parameters(self):
        return self.__alert_parameters

    @alert_parameters.setter
    def alert_parameters(self, value):
        if value is None:
            self.__alert_parameters = None
            return
        self.__alert_parameters = {
            "show_alert": bool(value["show_alert"]),
            "show_on_map": bool(value["show_on_map"]),
            "icon_signal_id": NameStr(
                value.get("icon_signal_id", {}).get("name", None)),
            "alert_message": value["alert_message"]
        }

    def to_json(self, obj):
        obj_set(obj, 'parameters', self.parameters)
        if self.alert_parameters is not None:
            sobj = {
                "show_alert": self.alert_parameters["show_alert"],
                "show_on_map": self.alert_parameters["show_on_map"],
                "alert_message": self.alert_parameters["alert_message"]}
            if self.alert_parameters["icon_signal_id"] is not None:
                sobj["icon_signal_id"] = {
                    "name": self.alert_parameters["icon_signal_id"],
                    "type": self.alert_parameters["icon_signal_id"].type}
            obj["alert_parameters"] = sobj
        return super().to_json(obj)


class Splitter(BaseMixin):
    def __init__(self, *args,
                 input_priority=None, output_priority=None, filter=None,
                 **kwargs):
        self.input_priority = input_priority
        self.output_priority = output_priority
        self.filter = filter
        super().__init__(*args, **kwargs)

    @property
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, value):
        self.__filter = NameStr(value)

    @property
    def input_priority(self):
        return self.__input_priority

    @input_priority.setter
    def input_priority(self, value):
        if value not in [None, "right", "left"]:
            raise ValueError(value)
        self.__input_priority = value

    @property
    def output_priority(self):
        return self.__output_priority

    @output_priority.setter
    def output_priority(self, value):
        if value not in [None, "right", "left"]:
            raise ValueError(value)
        self.__output_priority = value

    def to_json(self, obj):
        obj_set(obj, 'input_priority', self.input_priority)
        obj_set(obj, 'output_priority', self.output_priority)
        obj_set(obj, 'filter', self.filter)
        return super().to_json(obj)


class Station(CircuitCondition):
    class ControlBehavior:
        train_stopped_signal = SignalName()

        def __init__(self, *args, **kwargs):
            self.circuit_enable_disable = kwargs.pop(
                'circuit_enable_disable', None)
            self.read_from_train = kwargs.pop(
                'read_from_train', None)
            self.read_stopped_train = kwargs.pop(
                'read_stopped_train', None)
            self.train_stopped_signal = kwargs.pop(
                'train_stopped_signal', None)
            super().__init__(*args, **kwargs)

        def to_json(self, obj):
            obj_set(obj, 'circuit_enable_disable', self.circuit_enable_disable)
            obj_set(obj, 'read_from_train', self.read_from_train)
            obj_set(obj, 'read_stopped_train', self.read_stopped_train)
            if self.train_stopped_signal:
                obj_set(obj, 'train_stopped_signal',
                        self.train_stopped_signal.to_json())
            return super().to_json(obj)

    def __init__(self, *args, station=None, **kwargs):
        self.station = station
        super().__init__(*args, **kwargs)

    def to_json(self, obj):
        obj_set(obj, 'station', self.station)
        return super().to_json(obj)


class Underground(BaseMixin):
    def __init__(self, *args, type, **kwargs):
        self.type = type
        super().__init__(*args, **kwargs)

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value not in ["input", "output"]:
            raise ValueError(value)
        self.__type = value

    def to_json(self, obj):
        obj_set(obj, 'type', self.type)
        return super().to_json(obj)


class Loader(Underground):
    pass


class Variation(BaseMixin):
    def __init__(self, *args, variation=None, **kwargs):
        self.variation = variation
        super().__init__(*args, **kwargs)

    @property
    def variation(self):
        return self.__variation

    @variation.setter
    def variation(self, value):
        if value is not None and \
                value < 0 or value > 255:
            raise ValueError(value)
        self.__variation = value

    def to_json(self, obj):
        obj_set(obj, 'variation', self.variation)
        return super().to_json(obj)
