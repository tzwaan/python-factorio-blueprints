class InvalidExchangeString(Exception):
    pass


class UnknownPrototype(Exception):
    pass


class UnknownEntity(UnknownPrototype):
    pass


class UnknownRecipe(UnknownPrototype):
    pass


class UnknownSignal(UnknownPrototype):
    pass


class UnknownItem(UnknownPrototype):
    pass


class EntityOverlap(Exception):
    pass
