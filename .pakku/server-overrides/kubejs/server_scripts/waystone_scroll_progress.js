const MAX_TIME = 199 // One tick less than 10 seconds

// Safe API import
let MinecartHudApi = null
try {
  MinecartHudApi = Java.type('com.tyrthurey.minecartspeedfixes.api.MinecartHudApi')
} catch (e) {}

const active = new Map()

PlayerEvents.tick(event => {
  const player = event.player
  const uuid = String(player.uuid)

  // Not using scroll
  if (
    player.mainHandItem.id !== "waystones:bound_scroll" ||
    !player.isUsingItem()
  ) {
    if (active.has(uuid)) {
      active.delete(uuid)

      if (MinecartHudApi) {
        MinecartHudApi.unpauseHUD(player)
      }
    }
    return
  }

  // Start teleport
  if (!active.has(uuid)) {
    active.set(uuid, 0)

    if (MinecartHudApi) {
      MinecartHudApi.pauseHUD(player)
    }
  }

  let time = active.get(uuid) + 1
  active.set(uuid, time)

  let progress = Math.floor((time / MAX_TIME) * 10)

  let bar =
    "§a" + "█".repeat(progress) +
    "§7" + "█".repeat(10 - progress)

  player.displayClientMessage(`§aTeleporting... §f${bar}`, true)

  // Finish
  if (time >= MAX_TIME) {
    active.delete(uuid)

    if (MinecartHudApi) {
      MinecartHudApi.unpauseHUD(player)
    }
  }
})