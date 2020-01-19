from py_factorio_blueprints.util import namestr, Vector


class BaseMixin:
    def to_json(self):
        return {}


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

    def to_json(self):
        obj = super().to_json()
        if self.orientation is not None:
            obj["orientation"] = self.orientation
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.inventory is not None:
            obj['inventory'] = self.inventory
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.bar is not None:
            obj["bar"] = self.bar
        return obj


class Inserter(BaseMixin):
    def __init__(
            self, *args, override_stack_size=None, drop_position=None,
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

    def to_json(self):
        obj = super().to_json()
        if self.override_stack_size is not None:
            obj["override_stack_zize"] = self.override_stack_size
        if self.pickup_position is not None:
            obj["pickup_position"] = self.pickup_position.to_json()
        if self.drop_position is not None:
            obj["drop_position"] = self.drop_position.to_json()
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.filter_mode is not None:
            obj["filter_mode"] = self.filter_mode
        if self.filters:
            obj["filters"] = [
                {"index": index, "name": name}
                for index, name in self.filters.items()]
        return obj


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

    def to_json(self):
        obj = super().to_json()
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
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.items is not None:
            obj['items'] = self.items
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.recipe is not None:
            obj["recipe"] = self.recipe

        return obj


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

    def to_json(self):
        obj = super().to_json()
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
        return obj


class Rotatable(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate(self, amount, **kwargs):
        self.direction = self.direction.rotate(amount)
        sup = super()
        if hasattr(sup, "rotate"):
            next.rotate(amount, **kwargs)

    def to_json(self):
        obj = super().to_json()
        if not self.direction.isUp:
            obj['direction'] = self.direction
        return obj


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

    def to_json(self):
        obj = super().to_json()
        if self.input_priority is not None:
            obj["input_priority"] = self.input_priority
        if self.output_priority is not None:
            obj["output_priority"] = self.output_priority
        if self.filter is not None:
            obj["filter"] = self.filter
        return obj


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

    def to_json(self):
        obj = super().to_json()
        obj['type'] = self.type
        return obj


class Loader(Underground):
    pass

