ServerEvents.commandRegistry(event => {
    const { commands: Commands } = event;

    event.register(
        Commands.literal("ring")
            .executes(ctx => {
               const player = ctx.source.player

				player.tell("§5As your finger draws near, the ring seems to pulse with a heartbeat.")
				player.tell("")
				
				player.tell("§4§l\"Once accepted, our bond shall never be broken.\"")
				player.tell("")
				
				player.tell("§5No force may remove it. No spell may undo it.")
				player.tell("§5Not even death will free its bearer from its grasp.")
				player.tell("§5§lThere is no turning back.")
				
				player.tell("")
				player.tell("§4§lAre you absolutely certain whatever you are about to do is worth it?")
			
			
				player.give('enigmaticlegacyplus:cursed_ring')
				player.give('enigmaticlegacyplus:unwitnessed_amulet')
				
				return 1
            })
    )
})
