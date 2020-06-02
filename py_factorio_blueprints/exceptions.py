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


class UnknownTile(UnknownPrototype):
    pass


class DuplicateEntity(Exception):
    pass


class EntityOverlap(Exception):
    pass
