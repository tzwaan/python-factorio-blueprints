fluid = 'fluid'
item = 'item'
virtual = 'virtual'
tile = 'tile'
recipe = 'recipe'


defaultentities = {   # ADD MORE (vanilla) AS YOU PLEASE (or modded if it's just for you)!
                      # Somebody will probably automate the gathering of this data soon...

    'programmable-speaker': {
        'type': item,
        'width': 1,
        'height': 1,


        'parameters': True,
        'alertParameters': True
    },

    'heat-exchanger': {
        'type': item,
        'width': 3,
        'height': 2
    },

    'heat-pipe': {
        'type': item,
        'width': 1,
        'height': 1
    },

    'nuclear-reactor': {
        'type': item,
        'width': 5,
        'height': 5
    },

    'centrifuge': {
        'type': item,
        'width': 3,
        'height': 3
    },

    'steam-turbine': {
        'type': item,
        'width': 3,
        'height': 5
    },

    'tank': {
        'type': item
    },
    'car': {
        'type': item
    },
    'cargo-wagon': {
        'type': item,
        'inventorySize': 40
    },
    'fluid-wagon': {
        'type': item,
    },
    'locomotive': {
        'type': item
    },

    'light-armor': {
        'type': item
    },
    'heavy-armor': {
        'type': item
    },
    'modular-armor': {
        'type': item
    },
    'grenade': {
        'type': item
    },
    'cluster-grenade': {
        'type': item
    },
    'flamethrower': {
        'type': item
    },
    'flamethrower-ammo': {
        'type': item
    },
    'rocket-launcher': {
        'type': item
    },
    'rocket': {
        'type': item
    },
    'explosive-rocket': {
        'type': item
    },
    'atomic-bomb': {
        'type': item
    },
    'combat-shotgun': {
        'type': item
    },
    'shotgun': {
        'type': item
    },
    'shotgun-shell': {
        'type': item
    },
    'piercing-shotgun-shell': {
        'type': item
    },
    'submachine-gun': {
        'type': item
    },
    'pistol': {
        'type': item
    },
    'firearm-magazine': {
        'type': item
    },
    'piercing-rounds-magazine': {
        'type': item
    },
    'uranium-rounds-magazine': {
        'type': item
    },
    'cannon-shell': {
        'type': item
    },
    'explosive-cannon-shell': {
        'type': item
    },
    'uranium-cannon-shell': {
        'type': item
    },
    'explosive-uranium-cannon-shell': {
        'type': item
    },

    'power-armor': {
        'type': item
    },
    'power-armor-mk2': {
        'type': item
    },
    'energy-shield-equipment': {
        'type': item
    },
    'energy-shield-mk2-equipment': {
        'type': item
    },
    'solar-panel-equipment': {
        'type': item
    },
    'fusion-reactor-equipment': {
        'type': item
    },
    'battery-equipment': {
        'type': item
    },
    'battery-mk2-equipment': {
        'type': item
    },
    'personal-laser-defense-equipment': {
        'type': item
    },
    'discharge-defense-equipment': {
        'type': item
    },
    'exoskeleton-equipment': {
        'type': item
    },
    'personal-roboport-equipment': {
        'type': item
    },
    'personal-roboport-mk2-equipment': {
        'type': item
    },
    'night-vision-equipment': {
        'type': item
    },

    'discharge-defense-remote': {
        'type': item
    },
    'destroyer-capsule': {
        'type': item
    },
    'distractor-capsule': {
        'type': item
    },
    'defender-capsule': {
        'type': item
    },
    'slowdown-capsule': {
        'type': item
    },
    'poison-capsule': {
        'type': item
    },



    'stone': {
        'type': item
    },

    'solid-fuel': {
        'type': item
    },

    'stone-brick': {
        'type': item
    },

    'stone-path': {
        'type': tile
    },
    'landfill': {
        'type': item
    },
    'concrete': {
        'type': tile
    },
    'hazard-concrete': {
        'type': item
    },
    'hazard-concrete-left': {
        'type': tile
    },
    'hazard-concrete-right': {
        'type': tile
    },
    'refined-concrete': {
        'type': tile
    },
    'refined-hazard-concrete': {
        'type': item
    },
    'refined-hazard-concrete-left': {
        'type': tile
    },
    'refined-hazard-concrete-right': {
        'type': tile
    },

    'iron-axe': {
        'type': item
    },
    'steel-axe': {
        'type': item
    },
    'repair-pack': {
        'type': item
    },
    'blueprint': {
        'type': item
    },
    'deconstruction-planner': {
        'type': item
    },
    'blueprint-book': {
        'type': item
    },

    'copper-cable': {
        'type': item
    },
    'red-wire': {
        'type': item
    },
    'green-wire': {
        'type': item
    },

    'beacon': {
        'type': item,
        'width': 3,
        'height': 3,

        'modules': 2
    },
    'small-electric-pole': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'medium-electric-pole': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'substation': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'big-electric-pole': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'offshore-pump': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'small-lamp': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'solar-panel': {
        'type': item,
        'width': 3,
        'height': 3
    },
    'arithmetic-combinator': {
        'type': item,
        'width': 1,
        'height': 2
    },
    'decider-combinator': {
        'type': item,
        'width': 1,
        'height': 2
    },
    'constant-combinator': {
        'type': item,
        'width': 1,
        'height': 1
    },

    'splitter': {   # Default position is facing north, 2 wide and 1 high for all splitters.
        'type': item,
        'width': 2,
        'height': 1
    },
    'fast-splitter': {
        'type': item,
        'width': 2,
        'height': 1
    },
    'express-splitter': {
        'type': item,
        'width': 2,
        'height': 1
    },
    'transport-belt': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'fast-transport-belt': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'express-transport-belt': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'underground-belt': {
        'type': item,
        'width': 1,
        'height': 1,
        'directionType': True
    },
    'fast-underground-belt': {
        'type': item,
        'width': 1,
        'height': 1,
        'directionType': True
    },
    'express-underground-belt': {
        'type': item,
        'width': 1,
        'height': 1,
        'directionType': True
    },
    'assembling-machine-1': {
        'type': item,
        'width': 3,
        'height': 3,
        'recipe': True
    },
    'assembling-machine-2': {
        'type': item,
        'width': 3,
        'height': 3,

        'recipe': True,
        'modules': 2
    },
    'assembling-machine-3': {
        'type': item,
        'width': 3,
        'height': 3,

        'recipe': True,
        'modules': 4
    },
    'wooden-chest': {
        'type': item,
        'width': 1,
        'height': 1,

        'inventorySize': 16
    },
    'iron-chest': {
        'type': item,
        'width': 1,
        'height': 1,

        'inventorySize': 32
    },
    'steel-chest': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'logistic-chest-passive-provider': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'logistic-chest-active-provider': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'logistic-chest-storage': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'logistic-chest-requester': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'logistic-chest-buffer': {
        'type': item,
        'width': 1,
        'height': 1,
        'inventorySize': 48
    },
    'storage-tank': {
        'type': item,
        'width': 3,
        'height': 3
    },
    'burner-inserter': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'inserter': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'long-handed-inserter': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'fast-inserter': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'filter-inserter': {
        'type': item,
        'width': 1,
        'height': 1,
        'filterAmount': False
    },
    'stack-inserter': {
        'type': item,
        'width': 1,
        'height': 1,
    },
    'stack-filter-inserter': {
        'type': item,
        'width': 1,
        'height': 1,
        'filterAmount': False
    },
    'gate': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'stone-wall': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'radar': {
        'type': item,
        'width': 3,
        'height': 3
    },
    'rail': {
        'type': item
    },
    'straight-rail': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'curved-rail': {
        'type': item,
        'width': 1,
        'height': 1
    },
    # Lets figure out curved rails later. (1 curved rail deconstructs to 4 straight rails)
    'land-mine': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'train-stop': {  # pretty sure this is a 1.2x1.2 centered in a 2x2 square.
        'type': item,
        'width': 2,
        'height': 2
    },
    'rail-signal': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'rail-chain-signal': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'lab': {
        'type': item,
        'width': 3,
        'height': 3,

        'modules': 2
    },
    'rocket-silo': {
        'type': item,
        'width': 9,
        'height': 10,  # unsure about these values, got them from code only (never counted it in game, but 10 sounds right.)

        'modules': 4
    },
    'chemical-plant': {
        'type': item,
        'width': 3,
        'height': 3,

        'modules': 3
    },
    'oil-refinery': {
        'type': item,
        'width': 5,
        'height': 5,

        'modules': 3
    },
    'stone-furnace': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'steel-furnace': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'electric-furnace': {
        'type': item,
        'width': 3,
        'height': 3,

        'modules': 2
    },
    'pumpjack': {
        'type': item,
        'width': 3,
        'height': 3
    },
    'burner-mining-drill': {
        'type': item,
        'width': 2,
        'height': 2
    },

    'electric-mining-drill': {
        'type': item,
        'width': 3,
        'height': 3,

        'modules': 3
    },
    'pump': {
        'type': item,
        'width': 1,
        'height': 2
    },
    'pipe': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'pipe-to-ground': {
        'type': item,
        'width': 1,
        'height': 1
    },

    'electronic-circuit': {
        'type': item
    },
    'advanced-circuit': {
        'type': item
    },


    'boiler': {
        'type': item,
        'width': 1,
        'height': 1
    },
    'steam-engine': {
        'type': item,
        'width': 5,
        'height': 3
    },
    'accumulator': {
        'type': item,
        'width': 2,
        'height': 2
    },

    'roboport': {
        'type': item,
        'width': 4,
        'height': 4
    },
    'construction-robot': {
        'type': item
    },
    'logistic-robot': {
        'type': item
    },
    'power-switch': {
        'type': item,
        'width': 3,
        'height': 3
    },

    'gun-turret': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'laser-turret': {
        'type': item,
        'width': 2,
        'height': 2
    },
    'flamethrower-turret': {
        'type': item,
        'width': 2,
        'height': 3
    },


    'productivity-module': {
        'type': item
    },
    'productivity-module-2': {
        'type': item
    },
    'productivity-module-3': {
        'type': item
    },
    'effectivity-module': {
        'type': item
    },
    'effectivity-module-2': {
        'type': item
    },
    'effectivity-module-3': {
        'type': item
    },
    'speed-module': {
        'type': item
    },
    'speed-module-2': {
        'type': item
    },
    'speed-module-3': {
        'type': item
    },



    'water': {
        'type': fluid
    },
    'crude-oil': {
        'type': fluid
    },
    'petroleum-gas': {
        'type': fluid
    },
    'heavy-oil': {
        'type': fluid
    },
    'light-oil': {
        'type': fluid
    },
    'sulfuric-acid': {
        'type': fluid
    },
    'lubricant': {
        'type': fluid
    },
    'steam': {
        'type': fluid
    },

    'advanced-oil-processing': {
        'type': recipe
    },

    'raw-fish': {
        'type': item
    },
    'wood': {
        'type': item
    },
    'raw-wood': {
        'type': item
    },
    'iron-ore': {
        'type': item
    },
    'iron-plate': {
        'type': item
    },
    'copper-ore': {
        'type': item
    },
    'copper-plate': {
        'type': item
    },
    'steel-plate': {
        'type': item
    },
    'coal': {
        'type': item
    },
    'uranium-ore': {
        'type': item
    },
    'plastic-bar': {
        'type': item
    },
    'sulfur': {
        'type': item
    },

    'crude-oil-barrel': {
        'type': item
    },
    'heavy-oil-barrel': {
        'type': item
    },
    'light-oil-barrel': {
        'type': item
    },
    'lubricant-barrel': {
        'type': item
    },
    'petroleum-gas-barrel': {
        'type': item
    },
    'sulfuric-acid-barrel': {
        'type': item
    },
    'water-barrel': {
        'type': item
    },
    'empty-barrel': {
        'type': item
    },

    'processing-unit': {
        'type': item
    },

    'engine-unit': {
        'type': item
    },

    'electric-engine-unit': {
        'type': item
    },

    'battery': {
        'type': item
    },

    'explosives': {
        'type': item
    },
    'flying-robot-frame': {
        'type': item
    },
    'low-density-structure': {
        'type': item
    },
    'rocket-fuel': {
        'type': item
    },
    'rocket-control-unit': {
        'type': item
    },
    'satellite': {
        'type': item
    },
    'uranium-235': {
        'type': item
    },
    'uranium-238': {
        'type': item
    },

    'uranium-fuel-cell': {
        'type': item
    },
    'used-up-uranium-fuel-cell': {
        'type': item
    },
    'science-pack-1': {
        'type': item
    },
    'science-pack-2': {
        'type': item
    },
    'science-pack-3': {
        'type': item
    },
    'military-science-pack': {
        'type': item
    },
    'production-science-pack': {
        'type': item
    },
    'high-tech-science-pack': {
        'type': item
    },
    'space-science-pack': {
        'type': item
    },

    'iron-stick': {
        'type': item
    },
    'iron-gear-wheel': {
        'type': item
    },


    'signal-anything': {
        'type': virtual,
        'combinator': True
    },
    'signal-each': {
        'type': virtual,
        'combinator': True
    },
    'signal-everything': {
        'type': virtual,
        'combinator': True
    },
    'signal-0': {
        'type': virtual
    },
    'signal-1': {
        'type': virtual
    },
    'signal-2': {
        'type': virtual
    },
    'signal-3': {
        'type': virtual
    },
    'signal-4': {
        'type': virtual
    },
    'signal-5': {
        'type': virtual
    },
    'signal-6': {
        'type': virtual
    },
    'signal-7': {
        'type': virtual
    },
    'signal-8': {
        'type': virtual
    },
    'signal-9': {
        'type': virtual
    },
    'signal-A': {
        'type': virtual
    },
    'signal-B': {
        'type': virtual
    },
    'signal-C': {
        'type': virtual
    },
    'signal-D': {
        'type': virtual
    },
    'signal-E': {
        'type': virtual
    },
    'signal-F': {
        'type': virtual
    },
    'signal-G': {
        'type': virtual
    },
    'signal-H': {
        'type': virtual
    },
    'signal-I': {
        'type': virtual
    },
    'signal-J': {
        'type': virtual
    },
    'signal-K': {
        'type': virtual
    },
    'signal-L': {
        'type': virtual
    },
    'signal-M': {
        'type': virtual
    },
    'signal-N': {
        'type': virtual
    },
    'signal-O': {
        'type': virtual
    },
    'signal-P': {
        'type': virtual
    },
    'signal-Q': {
        'type': virtual
    },
    'signal-R': {
        'type': virtual
    },
    'signal-S': {
        'type': virtual
    },
    'signal-T': {
        'type': virtual
    },
    'signal-U': {
        'type': virtual
    },
    'signal-V': {
        'type': virtual
    },
    'signal-W': {
        'type': virtual
    },
    'signal-X': {
        'type': virtual
    },
    'signal-Y': {
        'type': virtual
    },
    'signal-Z': {
        'type': virtual
    },

    'signal-blue': {
        'type': virtual
    },
    'signal-red': {
        'type': virtual
    },
    'signal-green': {
        'type': virtual
    },
    'signal-yellow': {
        'type': virtual
    },
    'signal-cyan': {
        'type': virtual
    },
    'signal-pink': {
        'type': virtual
    },
    'signal-white': {
        'type': virtual
    },
    'signal-grey': {
        'type': virtual
    },
    'signal-black': {
        'type': virtual
    }
}
