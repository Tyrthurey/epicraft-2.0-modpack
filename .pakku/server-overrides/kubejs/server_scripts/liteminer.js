ServerEvents.tags('block', event => {
    event.add('liteminer:excluded_blocks', '#minecraft:logs')
})

ServerEvents.tags('item', event => {
    event.add('liteminer:excluded_tools', 'minecraft:wooden_pickaxe')
    event.add('liteminer:excluded_tools', 'minecraft:stone_pickaxe')
    event.add('liteminer:excluded_tools', 'minecraft:golden_pickaxe')
    event.add('liteminer:excluded_tools', 'minecraft:iron_pickaxe')

    event.add('liteminer:excluded_tools', 'simplest_paxels:wooden_paxel')
    event.add('liteminer:excluded_tools', 'simplest_paxels:stone_paxel')
    event.add('liteminer:excluded_tools', 'simplest_paxels:golden_paxel')
    event.add('liteminer:excluded_tools', 'simplest_paxels:iron_paxel')

})