from py_factorio_blueprints.entity_mixins import *

entity_prototypes = {
    'accumulator': {
        'mixins': [Accumulator]
    },
    'artillery-turret': {
        'mixins': [Rotatable]
    },
    'beacon': {
        'mixins': [Items]
    },
    'boiler': {
        'mixins': [Rotatable]
    },
    'burner-generator': {
        'mixins': [Rotatable]
    },
    'arithmetic-combinator': {
        'mixins': [Arithmetic, Rotatable],
    },
    'decider-combinator': {
        'mixins': [Decider, Rotatable],
    },
    'constant-combinator': {
        'mixins': [ConstantCombinator, Rotatable]
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
    'gate': {
        'mixins': [Rotatable]
    },
    'generator': {
        'mixins': [Rotatable]
    },
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
        'mixins': [MiningDrill, Rotatable]
    },
    'offshore-pump': {
        'mixins': [CircuitCondition, Rotatable]
    },
    'pipe': {},
    'infinity-pipe': {},
    'pipe-to-ground': {
        'mixins': [Rotatable]
    },
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
    'curved-rail': {
        'mixins': [Rotatable]
    },
    'straight-rail': {
        'mixins': [Rotatable]
    },
    'rail-chain-signal': {
        'mixins': [ChainSignal, Rotatable]
    },
    'rail-signal': {
        'mixins': [RailSignal, Rotatable]
    },
    'reactor': {},
    'roboport': {
        'mixins': [Roboport]
    },
    'simple-entity': {},
    'simple-entity-with-owner': {},
    'simple-entity-with-force': {},
    'solar-panel': {},
    'storage-tank': {
        'mixins': [Rotatable]
    },
    'train-stop': {
        'mixins': [Rotatable, Station, Color]
    },
    'loader-1x1': {
        'mixins': [Rotatable]
    },
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
        'mixins': [Train, Items],
    },
    'wall': {},
}
