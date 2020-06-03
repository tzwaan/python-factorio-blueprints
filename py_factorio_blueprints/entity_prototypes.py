from py_factorio_blueprints.entity_mixins import *

entity_prototypes = {
    'accumulator': {},
    'artillery-turret': {},
    'beacon': {},
    'boiler': {},
    'burner-generator': {},
    'arithmetic-combinator': {
        'mixins': [Arithmetic],
    },
    'decider-combinator': {
        'mixins': [Decider],
    },
    'constant-combinator': {},
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
        'mixins': [Rotatable, FilterInserter],
    },
    'lab': {},
    'lamp': {},
    'land-mine': {},
    'market': {},
    'mining-drill': {},
    'offshore-pump': {},
    'pipe': {},
    'infinity-pipe': {},
    'pipe-to-ground': {},
    'player-port': {},
    'power-switch': {},
    'programmable-speaker': {
        'mixins': [Speaker],
    },
    'pump': {},
    'radar': {},
    'curved-rail': {},
    'straight-rail': {},
    'rail-chain-signal': {},
    'rail-signal': {},
    'reactor': {},
    'roboport': {},
    'simple-entity': {},
    'simple-entity-with-owner': {},
    'simple-entity-with-force': {},
    'solar-panel': {},
    'storage-tank': {},
    'train-stop': {},
    'loader-1x1': {},
    'loader': {
        'mixins': [Rotatable, Loader],
    },
    'splitter': {
        'mixins': [Rotatable, Splitter]
    },
    'transport-belt': {
        'mixins': [Rotatable],
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
    'artillery-wagon': {},
    'cargo-wagon': {
        'mixins': [Rotatable, Cargo],
    },
    'fluid-wagon': {},
    'locomotive': {},
    'wall': {},
}
