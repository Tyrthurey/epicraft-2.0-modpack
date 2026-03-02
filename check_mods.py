import json
import sys
from pathlib import Path

def check_mod_platforms(filepath):
    """Check that all projects have both CurseForge and Modrinth entries."""

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data.get('projects', [])
    incomplete_mods = []

    for project in projects:
        # Get identifier for reporting
        name_data = project.get('name', {})
        slug_data = project.get('slug', {})
        id_data = project.get('id', {})

        # Determine display name (prefer Modrinth, fallback to CurseForge or ID)
        display_name = (
            name_data.get('modrinth') or 
            name_data.get('curseforge') or 
            slug_data.get('modrinth') or 
            slug_data.get('curseforge') or 
            project.get('pakku_id', 'Unknown')
        )

        missing_fields = []

        # Check slug
        if not slug_data.get('curseforge'):
            missing_fields.append('slug.curseforge')
        if not slug_data.get('modrinth'):
            missing_fields.append('slug.modrinth')

        # Check name
        if not name_data.get('curseforge'):
            missing_fields.append('name.curseforge')
        if not name_data.get('modrinth'):
            missing_fields.append('name.modrinth')

        # Check id
        if not id_data.get('curseforge'):
            missing_fields.append('id.curseforge')
        if not id_data.get('modrinth'):
            missing_fields.append('id.modrinth')

        if missing_fields:
            # Determine which platform is missing
            platforms = set()
            for field in missing_fields:
                if 'curseforge' in field:
                    platforms.add('CurseForge')
                elif 'modrinth' in field:
                    platforms.add('Modrinth')

            incomplete_mods.append({
                'name': display_name,
                'pakku_id': project.get('pakku_id', 'N/A'),
                'missing_fields': missing_fields,
                'missing_platforms': list(platforms)
            })

    return incomplete_mods

def main():
    filepath = Path("./pakku-lock.json")

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        

    incomplete = check_mod_platforms(filepath)

    if not incomplete:
        print("✓ All mods have both CurseForge and Modrinth counterparts")
        return 0

    print(f"Found {len(incomplete)} mod(s) missing platform counterparts:\n")

    for mod in incomplete:
        print(f"• {mod['name']}")
        print(f"  Pakku ID: {mod['pakku_id']}")

        if len(mod['missing_platforms']) == 1:
            print(f"  Status: Only available on {mod['missing_platforms'][0]}")
        else:
            print(f"  Missing fields: {', '.join(mod['missing_fields'])}")
        print()

    return 1

if __name__ == "__main__":
    sys.exit(main())
