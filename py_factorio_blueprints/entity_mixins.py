from py_factorio_blueprints.util import (
    namestr, Vector, Color as ColorObj, Condition)


class BaseMixin:
    def to_json(self, obj):
        return obj


class Train(BaseMixin):
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
        if self.orientation is not None:
            obj["orientation"] = self.orientation
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
        return self.__bar

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
        if self.__inventory_bar:
            inventory["bar"] = self.__inventory_bar
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
        for filter in value.get("filters", []):
            self.__inventory_filters[filter["index"]] = namestr(filter["name"])

    def to_json(self, obj):
        if self.inventory is not None:
            obj['inventory'] = self.inventory
        return super().to_json(obj)


class Color(BaseMixin):
    def __init__(self, *args, color=None, **kwargs):
        self.color = color
        super().__init__(*args, **kwargs)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if value is None:
            self.__color = None
        self.__color = ColorObj(**value)

    def to_json(self, obj):
        if self.color is not None:
            obj["color"] = self.color.to_json()
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
        if self.bar is not None:
            obj["bar"] = self.bar
        return super().to_json(obj)


class CircuitCondition(BaseMixin):
    def __init__(self, *args, **kwargs):
        if "control_behavior" in kwargs:
            circuit_condition = kwargs["control_behavior"].pop("circuit_condition")
            if not kwargs["control_behavior"]:
                kwargs.pop("control_behavior")
            self.circuit_condition = circuit_condition
        else:
            self.circuit_condition = None
        super().__init__(*args, **kwargs)

    @property
    def circuit_condition(self):
        return self.__circuit_condition

    @circuit_condition.setter
    def circuit_condition(self, value):
        if isinstance(value, dict):
            self.__circuit_condition = Condition(**value)
        elif isinstance(value, Condition):
            self.__circuit_condition = value
        else:
            self.__circuit_condition = None

    def to_json(self, obj):
        if self.circuit_condition is not None:
            if "control_behavior" not in obj:
                obj["control_behavior"] = {}
            obj["control_behavior"]["circuit_condition"] = \
                self.circuit_condition.to_json()
        return super().to_json(obj)


class Inserter(BaseMixin):
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
        if self.override_stack_size is not None:
            obj["override_stack_zize"] = self.override_stack_size
        if self.pickup_position is not None:
            obj["pickup_position"] = self.pickup_position.to_json()
        if self.drop_position is not None:
            obj["drop_position"] = self.drop_position.to_json()
        return super().to_json(obj)


class FilterInserter(Inserter):
    def __init__(self, *args, filters=None, filter_mode=None, **kwargs):
        self.filters = filters
        self.filter_mode = filter_mode
        super().__init__(*args, **kwargs)

    @property
    def filters(self):
        return self.__filters

    @filters.setter
    def filters(self, values):
        self.__filters = {}
        if values is None:
            values = []
        for value in values:
            self.__filters[value["index"]] = namestr(value["name"])

    @property
    def filter_mode(self):
        return self.__filter_mode

    @filter_mode.setter
    def filter_mode(self, value):
        if value not in [None, "whitelist", "blacklist"]:
            raise ValueError(value)
        self.__filter_mode = value

    def to_json(self, obj):
        if self.filter_mode is not None:
            obj["filter_mode"] = self.filter_mode
        if self.filters:
            obj["filters"] = [
                {"index": index, "name": name}
                for index, name in self.filters.items()]
        return super().to_json(obj)


class InfinityContainer(BaseMixin):
    def __init__(self, *args, infinity_settings=None, **kwargs):
        self.infinity_settings = infinity_settings
        super().__init__(*args, **kwargs)

    @property
    def infinity_settings(self):
        return {
            "remove_unfiltered_items": self.infinity_settings_remove_unfiltered_items,
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
                "name": namestr(value["name"])
            }

    def to_json(self, obj):
        if self.infinity_settings:
            obj["infinity_settings"] = {
                "remove_unfiltered_items": self.infinity_settings_remove_unfiltered_items,
                "filters": [
                    {
                        "index": index,
                        "count": value["count"],
                        "mode": value["mode"],
                        "name": value["name"]
                    }
                    for index, value in self.infinity_settings_filters.items()
                ]
            }
        return super().to_json(obj)


class Items(BaseMixin):
    def __init__(self, *args, items=None, **kwargs):
        if items is None:
            items = {}
        self.__items = {}
        for item, amount in items.items():
            self.items[namestr(item)] = amount
        super().__init__(*args, **kwargs)

    @property
    def items(self):
        return self.__items

    def to_json(self, obj):
        if self.items is not None:
            obj['items'] = self.items
        return super().to_json(obj)


class Recipe(BaseMixin):
    def __init__(self, *args, recipe=None, **kwargs):
        self.recipe = recipe
        super().__init__(*args, **kwargs)

    @property
    def recipe(self):
        return self.__recipe

    @recipe.setter
    def recipe(self, value):
        self.__recipe = namestr(value)

    def to_json(self, obj):
        if self.recipe is not None:
            obj["recipe"] = self.recipe
        return super().to_json(obj)


class Requester(BaseMixin):
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
                "name": namestr(value["name"]),
                "count": int(value["count"])
            }

    def to_json(self, obj):
        obj["request_from_buffers"] = self.request_from_buffers
        if self.request_filters:
            obj["request_filters"] = [
                {
                    "index": index,
                    "name": filter["name"],
                    "count": filter["count"]
                }
                for index, filter in self.request_filters.items()
            ]
        return super().to_json(obj)


class Rotatable(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate(self, amount, **kwargs):
        self.direction = self.direction.rotate(amount)
        sup = super()
        if hasattr(sup, "rotate"):
            next.rotate(amount, **kwargs)

    def to_json(self, obj):
        if not self.direction.isUp:
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
        if self.auto_launch is not None:
            obj["auto_launch"] = self.auto_launch
        return super().to_json(obj)


class Speaker(BaseMixin):
    def __init__(self, *args, parameters=None, alert_parameters=None, **kwargs):
        self.parameters = parameters
        self.alert_parameters = alert_parameters
        if "control_behavior" in kwargs:
            circuit_parameters = kwargs["control_behavior"].pop("circuit_parameters")
            if not kwargs["control_behavior"]:
                kwargs.pop("control_behavior")
            self.circuit_parameters = circuit_parameters
        else:
            self.circuit_parameters = None
        super().__init__(*args, **kwargs)

    @property
    def circuit_parameters(self):
        return self.__circuit_parameters

    @circuit_parameters.setter
    def circuit_parameters(self, value):
        if value is None:
            self.__circuit_parameters = None
            return
        self.__circuit_parameters = {
            "signal_value_is_pitch": bool(value["signal_value_is_pitch"]),
            "instrument_id": int(value["instrument_id"]),
            "note_id": int(value["note_id"])}

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
            "icon_signal_id": namestr(
                value.get("icon_signal_id", {}).get("name", None)),
            "alert_message": value["alert_message"]
        }

    def to_json(self, obj):
        if self.parameters is not None:
            obj["parameters"] = self.parameters
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
        if self.circuit_parameters is not None:
            if "control_behavior" not in obj:
                obj["control_behavior"] = {}
            obj["control_behavior"]["circuit_parameters"] = \
                self.circuit_parameters
        return super().to_json(obj)


class Splitter(BaseMixin):
    def __init__(self, *args, input_priority=None, output_priority=None, filter=None, **kwargs):
        self.input_priority = input_priority
        self.output_priority = output_priority
        self.filter = filter
        super().__init__(*args, **kwargs)

    @property
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, value):
        self.__filter = namestr(value)

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
        if self.input_priority is not None:
            obj["input_priority"] = self.input_priority
        if self.output_priority is not None:
            obj["output_priority"] = self.output_priority
        if self.filter is not None:
            obj["filter"] = self.filter
        return super().to_json(obj)


class Station(BaseMixin):
    def __init__(self, *args, station=None, **kwargs):
        self.station = station
        super().__init__(*args, **kwargs)

    @property
    def station(self):
        return self.__station

    @station.setter
    def station(self, value):
        self.__station = value

    def to_json(self, obj):
        if self.station is not None:
            obj["station"] = self.station
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
        obj['type'] = self.type
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
        if self.variation is not None:
            obj["variation"] = self.variation
        return super().to_json(obj)

