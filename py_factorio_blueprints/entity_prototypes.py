from py_factorio_blueprints.entity_mixins import *

entity_prototypes = {
    'accumulator': {
        'mixins': [Accumulator]
    },
    'artillery-turret': {},
    'beacon': {
        'mixins': [Items]
    },
    'boiler': {},
    'burner-generator': {},
    'arithmetic-combinator': {
        'mixins': [Arithmetic],
    },
    'decider-combinator': {
        'mixins': [Decider],
    },
    'constant-combinator': {
        'mixins': [ConstantCombinator]
    },
    'container': {},
    'logistic-container': {
        'mixins': [Requester],
    },
    'infinity-container': {
        'mixins': [InfinityContainer],
    },
    'assembling-machine': {
        'mixins': [Rotatable, Recipe],
    },
    'rocket-silo': {
        'mixins': [Silo],
    },
    'furnace': {},
    'electric-energy-interface': {},
    'electric-pole': {},
    'gate': {},
    'generator': {},
    'heat-interface': {},
    'heat-pipe': {},
    'inserter': {
        'mixins': [CircuitCondition, FilterInserter, Rotatable],
    },
    'lab': {},
    'lamp': {
        'mixins': [Lamp]
    },
    'land-mine': {},
    'market': {},
    'mining-drill': {
        'mixins': [MiningDrill]
    },
    'offshore-pump': {
        'mixins': [CircuitCondition]
    },
    'pipe': {},
    'infinity-pipe': {},
    'pipe-to-ground': {},
    'player-port': {},
    'power-switch': {
        'mixins': [CircuitCondition]
    },
    'programmable-speaker': {
        'mixins': [Speaker],
    },
    'pump': {
        'mixins': [Rotatable, CircuitCondition]
    },
    'radar': {},
    'curved-rail': {},
    'straight-rail': {},
    'rail-chain-signal': {
        'mixins': [ChainSignal]
    },
    'rail-signal': {
        'mixins': [RailSignal]
    },
    'reactor': {},
    'roboport': {
        'mixins': [Roboport]
    },
    'simple-entity': {},
    'simple-entity-with-owner': {},
    'simple-entity-with-force': {},
    'solar-panel': {},
    'storage-tank': {},
    'train-stop': {
        'mixins': [Rotatable, Station, Color]
    },
    'loader-1x1': {},
    'loader': {
        'mixins': [Rotatable, Loader],
    },
    'splitter': {
        'mixins': [Rotatable, Splitter]
    },
    'transport-belt': {
        'mixins': [Rotatable, TransportBelt, CircuitCondition],
    },
    'underground-belt': {
        'mixins': [Rotatable, Underground],
    },
    'turret': {
        'mixins': [Rotatable],
    },
    'ammo-turret': {
        'mixins': [Rotatable],
    },
    'electric-turret': {
        'mixins': [Rotatable],
    },
    'fluid-turret': {
        'mixins': [Rotatable],
    },
    'vehicle': {},
    'car': {},
    'artillery-wagon': {
        'mixins': [Train],
    },
    'cargo-wagon': {
        'mixins': [Cargo],
    },
    'fluid-wagon': {
        'mixins': [Train],
    },
    'locomotive': {
        'mixins': [Train],
    },
    'wall': {},
}
