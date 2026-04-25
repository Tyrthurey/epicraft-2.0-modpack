// Plushie Buddies - Mob Drop LootJS Script
LootJS.modifiers((event) => {
    // Allay - 1%
    event.addEntityModifier("minecraft:allay").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_allay").limitCount(1, 1));
    // Armadillo - 1%
    event.addEntityModifier("minecraft:armadillo").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_armadillo").limitCount(1, 1));
    // Axolotl - 1%
    event.addEntityModifier("minecraft:axolotl").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_axolotl").limitCount(1, 1));
    // Bat - 1%
    event.addEntityModifier("minecraft:bat").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_bat").limitCount(1, 1)).randomChance(0.5).addLoot(LootEntry.of("minecraft:phantom_membrane").limitCount(1, 1));
    // Bee - 1%
    event.addEntityModifier("minecraft:bee").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_bee").limitCount(1, 1));
    // Blaze - 0.1%
    event.addEntityModifier("minecraft:blaze").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_blaze").limitCount(1, 1));
    // Breeze - 0.1%
    event.addEntityModifier("minecraft:breeze").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_breeze").limitCount(1, 1));
    // Camel - 1%
    event.addEntityModifier("minecraft:camel").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_camel").limitCount(1, 1));
    // Cat - 1%
    event.addEntityModifier("minecraft:cat").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_cat").limitCount(1, 1));
    // Cave Spider - 0.1%
    event.addEntityModifier("minecraft:cave_spider").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_cave_spider").limitCount(1, 1));
    // Chicken - 0.1%
    event.addEntityModifier("minecraft:chicken").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_chicken").limitCount(1, 1));
    // Cow - 0.1%
    event.addEntityModifier("minecraft:cow").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_cow").limitCount(1, 1));
    // Creeper - 1%
    event.addEntityModifier("minecraft:creeper").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_creeper").limitCount(1, 1));
    // Dolphin - 10%
    event.addEntityModifier("minecraft:dolphin").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_dolphin").limitCount(1, 1));
    // Donkey - 1%
    event.addEntityModifier("minecraft:donkey").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_donkey").limitCount(1, 1));
    // Drowned - 0.1%
    event.addEntityModifier("minecraft:drowned").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_drowned").limitCount(1, 1));
    // Elder Guardian - 25%
    event.addEntityModifier("minecraft:elder_guardian").randomChance(0.25).addLoot(LootEntry.of("plushie_buddies:plushie_elder_guardian").limitCount(1, 1));
    // Ender Dragon - 100% (4 drops)
    event.addEntityModifier("minecraft:ender_dragon").randomChance(1.0).addLoot(LootEntry.of("plushie_buddies:plushie_enderdragon").limitCount(4, 4));
    // Enderman - 0.1%
    event.addEntityModifier("minecraft:enderman").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_enderman").limitCount(1, 1));
    // Evoker - 10%
    event.addEntityModifier("minecraft:evoker").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_evoker").limitCount(1, 1));
    // Fox - 1%
    event.addEntityModifier("minecraft:fox").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_fox").limitCount(1, 1));
    // Frog - 1%
    event.addEntityModifier("minecraft:frog").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_frog").limitCount(1, 1));
    // Ghast - 10%
    event.addEntityModifier("minecraft:ghast").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_ghast").limitCount(1, 1));
    // Glow Squid - 5%
    event.addEntityModifier("minecraft:glow_squid").randomChance(0.05).addLoot(LootEntry.of("plushie_buddies:plushie_glow_squid").limitCount(1, 1));
    // Goat - 1%
    event.addEntityModifier("minecraft:goat").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_goat").limitCount(1, 1));
    // Guardian - 1%
    event.addEntityModifier("minecraft:guardian").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_guardian").limitCount(1, 1));
    // Hoglin - 1%
    event.addEntityModifier("minecraft:hoglin").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_hoglin").limitCount(1, 1));
    // Horse - 1%
    event.addEntityModifier("minecraft:horse").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_horse").limitCount(1, 1));
    // Husk - 1%
    event.addEntityModifier("minecraft:husk").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_husk").limitCount(1, 1));
    // Iron Golem - 5%
    event.addEntityModifier("minecraft:iron_golem").randomChance(0.05).addLoot(LootEntry.of("plushie_buddies:plushie_iron_golem").limitCount(1, 1));
    // Llama - 2%
    event.addEntityModifier("minecraft:llama").randomChance(0.02).addLoot(LootEntry.of("plushie_buddies:plushie_llama").limitCount(1, 1));
    // Magma Cube - 1%
    event.addEntityModifier("minecraft:magma_cube").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_magma_cube").limitCount(1, 1));
    // Mooshroom - 1%
    event.addEntityModifier("minecraft:mooshroom").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_mooshroom").limitCount(1, 1));
    // Mule - 1%
    event.addEntityModifier("minecraft:mule").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_mule").limitCount(1, 1));
    // Panda - 2%
    event.addEntityModifier("minecraft:panda").randomChance(0.02).addLoot(LootEntry.of("plushie_buddies:plushie_panda").limitCount(1, 1));
    // Parrot - 2%
    event.addEntityModifier("minecraft:parrot").randomChance(0.02).addLoot(LootEntry.of("plushie_buddies:plushie_parrot").limitCount(1, 1));
    // Phantom - 1%
    event.addEntityModifier("minecraft:phantom").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_phantom").limitCount(1, 1));
    // Pig - 0.1%
    event.addEntityModifier("minecraft:pig").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_pig").limitCount(1, 1));
    // Piglin Brute - 5%
    event.addEntityModifier("minecraft:piglin_brute").randomChance(0.05).addLoot(LootEntry.of("plushie_buddies:plushie_piglin_brute").limitCount(1, 1));
    // Piglin - 1%
    event.addEntityModifier("minecraft:piglin").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_piglin").limitCount(1, 1));
    // Pillager - 1%
    event.addEntityModifier("minecraft:pillager").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_pillager").limitCount(1, 1));
    // Polar Bear - 1%
    event.addEntityModifier("minecraft:polar_bear").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_polar_bear").limitCount(1, 1));
    // Pufferfish - 10%
    event.addEntityModifier("minecraft:pufferfish").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_pufferfish").limitCount(1, 1));
    // Rabbit - 1%
    event.addEntityModifier("minecraft:rabbit").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_rabbit").limitCount(1, 1));
    // Ravager - 20%
    event.addEntityModifier("minecraft:ravager").randomChance(0.2).addLoot(LootEntry.of("plushie_buddies:plushie_ravanger").limitCount(1, 1));
    // Sheep - 0.1%
    event.addEntityModifier("minecraft:sheep").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_sheep").limitCount(1, 1));
    // Shulker - 5%
    event.addEntityModifier("minecraft:shulker").randomChance(0.05).addLoot(LootEntry.of("plushie_buddies:plushie_shulker").limitCount(1, 1));
    // Skeleton Horse - 50%
    event.addEntityModifier("minecraft:skeleton_horse").randomChance(0.5).addLoot(LootEntry.of("plushie_buddies:plushie_skeleton_horse").limitCount(1, 1));
    // Skeleton - 0.1%
    event.addEntityModifier("minecraft:skeleton").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_skeleton").limitCount(1, 1));
    // Slime - 1%
    event.addEntityModifier("minecraft:slime").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_slime").limitCount(1, 1));
    // Sniffer - 50%
    event.addEntityModifier("minecraft:sniffer").randomChance(0.5).addLoot(LootEntry.of("plushie_buddies:plushie_sniffer").limitCount(1, 1));
    // Spider - 0.1%
    event.addEntityModifier("minecraft:spider").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_spider").limitCount(1, 1));
    // Squid - 1%
    event.addEntityModifier("minecraft:squid").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_squid").limitCount(1, 1));
    // Stray - 1%
    event.addEntityModifier("minecraft:stray").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_stray").limitCount(1, 1));
    // Strider - 5%
    event.addEntityModifier("minecraft:strider").randomChance(0.05).addLoot(LootEntry.of("plushie_buddies:plushie_strider").limitCount(1, 1));
    // Trader Llama - 50%
    event.addEntityModifier("minecraft:trader_llama").randomChance(0.5).addLoot(LootEntry.of("plushie_buddies:plushie_trader_lama").limitCount(1, 1));
    // Turtle - 1%
    event.addEntityModifier("minecraft:turtle").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_turtle").limitCount(1, 1));
    // Vex - 10%
    event.addEntityModifier("minecraft:vex").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_vex").limitCount(1, 1));
    // Villager - 2%
    event.addEntityModifier("minecraft:villager").randomChance(0.02).addLoot(LootEntry.of("plushie_buddies:plushie_villager").limitCount(1, 1));
    // Vindicator - 25%
    event.addEntityModifier("minecraft:vindicator").randomChance(0.25).addLoot(LootEntry.of("plushie_buddies:plushie_vindicator").limitCount(1, 1));
    // Wandering Trader - 50%
    event.addEntityModifier("minecraft:wandering_trader").randomChance(0.5).addLoot(LootEntry.of("plushie_buddies:plushie_wandering_trader").limitCount(1, 1));
    // Warden - 100%
    event.addEntityModifier("minecraft:warden").randomChance(1.0).addLoot(LootEntry.of("plushie_buddies:plushie_warden").limitCount(1, 1));
    // Witch - 20%
    event.addEntityModifier("minecraft:witch").randomChance(0.2).addLoot(LootEntry.of("plushie_buddies:plushie_witch").limitCount(1, 1));
    // Wither Skeleton - 1%
    event.addEntityModifier("minecraft:wither_skeleton").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_wither_skeleton").limitCount(1, 1));
    // Wither - 30%
    event.addEntityModifier("minecraft:wither").randomChance(0.3).addLoot(LootEntry.of("plushie_buddies:plushie_wither").limitCount(1, 1));
    // Wolf - 1%
    event.addEntityModifier("minecraft:wolf").randomChance(0.01).addLoot(LootEntry.of("plushie_buddies:plushie_wolf").limitCount(1, 1));
    // Zoglin - 20%
    event.addEntityModifier("minecraft:zoglin").randomChance(0.2).addLoot(LootEntry.of("plushie_buddies:plushie_zoglin").limitCount(1, 1));
    // Zombie Villager - 10%
    event.addEntityModifier("minecraft:zombie_villager").randomChance(0.1).addLoot(LootEntry.of("plushie_buddies:plushie_zombie_villager").limitCount(1, 1));
    // Zombie - 0.1%
    event.addEntityModifier("minecraft:zombie").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_zombie").limitCount(1, 1));
    // Zombified Piglin - 0.1%
    event.addEntityModifier("minecraft:zombified_piglin").randomChance(0.001).addLoot(LootEntry.of("plushie_buddies:plushie_zombified_piglin").limitCount(1, 1));
});
