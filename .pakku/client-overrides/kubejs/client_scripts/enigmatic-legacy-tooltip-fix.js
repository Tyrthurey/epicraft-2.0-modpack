ItemEvents.modifyTooltips(event => {
  event.modify('enigmaticlegacyplus:etherium_scythe', tooltip => {
    tooltip.removeLine(1)
    tooltip.insert(1, Text.of('Tills blocks in a 3x3 area.').color(0xAA00AA))
    tooltip.removeLine(2)
    tooltip.insert(2, Text.of('Hold Shift to suppress this effect.').color(0xAA00AA))
  })
})