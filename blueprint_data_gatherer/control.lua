require("json")
 
function getEnergyData(prototype, data)
    if prototype.burner_prototype ~= nil then
        data["burner_effectivity"]=prototype.burner_prototype.effectivity
        data["fuel_categories"]=prototype.burner_prototype.fuel_categories
        data["emissions"]=prototype.burner_prototype.emissions
    elseif prototype.electric_energy_source_prototype ~= nil then
        data["drain"]=prototype.electric_energy_source_prototype.drain*60
        data["emissions"]=prototype.electric_energy_source_prototype.emissions
    end
    return data
end

function has_value(iterable, val)
    for key, value in ipairs(iterable) do
        if value == val then
            return true
        end
    end
    return false
end

gatherer_entity_prototypes = {
    'accumulator',
    'artillery-turret',
    'beacon',
    'boiler',
    'burner-generator',
    'arithmetic-combinator',
    'decider-combinator',
    'constant-combinator',
    'container',
    'logistic-container',
    'infinity-container',
    'assembling-machine',
    'rocket-silo',
    'furnace',
    'electric-energy-interface',
    'electric-pole',
    'gate',
    'generator',
    'heat-interface',
    'heat-pipe',
    'inserter',
    'lab',
    'lamp',
    'land-mine',
    'market',
    'mining-drill',
    'offshore-pump',
    'pipe',
    'infinity-pipe',
    'pipe-to-ground',
    'player-port',
    'power-switch',
    'programmable-speaker',
    'pump',
    'radar',
    'curved-rail',
    'straight-rail',
    'rail-chain-signal',
    'rail-signal',
    'reactor',
    'roboport',
    'simple-entity',
    'simple-entity-with-owner',
    'simple-entity-with-force',
    'solar-panel',
    'storage-tank',
    'train-stop',
    'loader-1x1',
    'loader',
    'splitter',
    'transport-belt',
    'underground-belt',
    'turret',
    'ammo-turret',
    'electric-turret',
    'fluid-turret',
    'vehicle',
    'car',
    'artillery-wagon',
    'cargo-wagon',
    'fluid-wagon',
    'locomotive',
    'wall',
}

gatherer_entity_fields = {
    "name",
    "type",
    "localised_name",
    "localised_description",
    "flags",
    "selection_box",
    "items_to_place_this",
}

gatherer_recipe_fields = {
    "name",
    "localised_name",
    "localised_description"
}

function gather_prototype_data(data, prototypes, fields)
    local outdata = {}
    for name,prototype in pairs(data) do
        if not prototypes or has_value(prototypes, prototype['type']) then
            log(name)
            outdata[name] = {}
            for _, field in pairs(fields) do
                outdata[name][field] = prototype[field]
            end
        end
    end

    return outdata
end

function gather_signal_data()
    local outdata = {}
    for _, prototype in pairs(game.virtual_signal_prototypes) do
        outdata[prototype.name] = {
            name=prototype.name,
            type='virtual'
        }
    end
    for _, prototype in pairs(game.fluid_prototypes) do
        if not prototype.hidden then
            outdata[prototype.name] = {
                name=prototype.name,
                type='fluid'
            }
        end
    end
    for _, prototype in pairs(game.item_prototypes) do
        if not prototype.has_flag('hidden') then
            outdata[prototype.name] = {
                name=prototype.name,
                type='item'
            }
        end
    end
    return outdata
end

function gather_data()
    local outdata = {}
    outdata['entity'] = gather_prototype_data(
        game.entity_prototypes,
        gatherer_entity_prototypes,
        gatherer_entity_fields)
    outdata['recipe'] = gather_prototype_data(
        game.recipe_prototypes,
        false,
        gatherer_recipe_fields)
    outdata['signal'] = gather_signal_data()
    return outdata
end

function write_data(outdata)
    local folder = "blueprint-data-gatherer"
    local filename = "entity_data.json"
    game.write_file(
        folder.."/"..filename,
        global.json.stringify(outdata))
end
 
script.on_event(
    defines.events.on_player_created,
    function(event)
        local playersettings = settings.get_player_settings(
                game.players[event.player_index])
            if playersettings["blueprint-data-gatherer-disabled"].value then
                log("Skipping data gathering")
            else
                write_data(gather_data())
                game.players[event.player_index].print{"recipe.hi"}
            return
        end
    end
)