MoreJS.enchantmentTableChanged(event => {
    const blocked = [
        "enchantencore:phantom_menace",
        "enchantencore:moonwalk",
        "enchantencore:safe_landing",
        "enchantencore:pegasus",
        "nova_structures:wax_wings"
    ]

    let data;
    for (let i = 0; i < 3; i++) {
        data = event.get(i)

        data.removeEnchantments((enchantment) =>
            blocked.includes(enchantment.getKey().location().toString())
        )

        data.randomClue()
    }
})