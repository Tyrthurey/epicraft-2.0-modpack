const BUILD_LIMIT = 1500
const WILD_LIMIT = 2000
const CHECK_INTERVAL = 100 // 5 seconds

let playerZones = {}
let playerTimers = {}

function getZone(x, z) {
    const maxCoord = Math.max(Math.abs(Math.floor(x)), Math.abs(Math.floor(z)))

    if (maxCoord < BUILD_LIMIT) return "build"
    if (maxCoord < WILD_LIMIT) return "transition"
    return "wilderness"
}

PlayerEvents.tick(event => {
    const player = event.player
    if (!player || player.level.isClientSide()) return

    const uuid = player.uuid

    if (!playerTimers[uuid]) playerTimers[uuid] = 0
    playerTimers[uuid]++

    if (playerTimers[uuid] < CHECK_INTERVAL) return
    playerTimers[uuid] = 0

    const zone = getZone(player.x, player.z)

    if (!playerZones[uuid]) {
        playerZones[uuid] = zone
        return
    }

    if (playerZones[uuid] !== zone) {

        let titleData = {}

        if (zone === "build") {
            titleData = { text: "Safe Zone", color: "dark_green" }
        }
        else if (zone === "transition") {
            titleData = { text: "Transition Zone", color: "gold" }
        }
        else {
            titleData = { text: "Wilderness", color: "dark_red" }
        }

        player.server.runCommandSilent(
            `title ${player.username} title ${JSON.stringify(titleData)}`
        )

        playerZones[uuid] = zone
    }
})

ServerEvents.commandRegistry(event => {
    const { commands: Commands } = event;

    event.register(
        Commands.literal("zone")
            .executes(ctx => {

                const player = ctx.source.player

                const zone = getZone(player.x, player.z)

                let titleData = {}

                if (zone === "build") {
                    titleData = { text: "Build Zone", color: "green" }
                }
                else if (zone === "transition") {
                    titleData = { text: "Transition Zone", color: "gold" }
                }
                else {
                    titleData = { text: "Wilderness", color: "red" }
                }

                player.server.runCommandSilent(
                    `title ${player.username} title ${JSON.stringify(titleData)}`
                )

                return 1
            })
    )
})

