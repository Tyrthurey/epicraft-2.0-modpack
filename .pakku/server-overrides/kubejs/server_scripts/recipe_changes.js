// Listen for the "recipes" server event.
ServerEvents.recipes(event => {

    // Gilded blackstone

    event.shaped(
        Item.of('minecraft:gilded_blackstone', 1),
        [
            'AAA',
            'ABA',
            'AAA'
        ],
        {
            A: 'minecraft:gold_nugget',
            B: 'minecraft:blackstone',
        }
    )

	// Blank scroll	
	event.remove({ output: 'waystones:warp_scroll' })

    event.shaped(
        Item.of('waystones:warp_scroll', 3),
        [
            'ESE',
			'STS',
			'ENE'
        ],
        {
            E: 'minecraft:ender_pearl',
            T: 'minecraft:totem_of_undying',
			S: 'minecraft:echo_shard',
			N: 'netherite_scrap'
        }
    )
})		