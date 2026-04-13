import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


def load_env_file() -> None:
    """Load .env file into environment variables."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip().strip("\"'")
                    if key and value:
                        os.environ[key] = value


# Load .env file at startup
load_env_file()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via DEBUG env var."""
    return os.environ.get("DEBUG", "").lower() == "true"


def debug_print(*args, **kwargs):
    """Print only if debug mode is enabled."""
    if is_debug_mode():
        print(*args, **kwargs)


def use_curseforge_api() -> bool:
    """Check if CurseForge API should be used."""
    # Check env var first, then fall back to checking if API key exists
    use_cf = os.environ.get("USE_CURSEFORGE_API", "").lower()
    if use_cf == "true":
        return True
    elif use_cf == "false":
        return False
    # Default: check if API key exists
    return bool(os.environ.get("CURSEFORGE_API_KEY"))


# API Configuration
MODRINTH_API_URL = "https://api.modrinth.com/v2"
CURSEFORGE_API_URL = "https://api.curseforge.com/v1"
ENV_FILE = Path(".env")
PAKKU_JAR = Path("pakku.jar")
PAKKU_RELEASES_URL = "https://github.com/juraj-hrivnak/Pakku/releases/latest"


def load_curseforge_only_exceptions() -> set[str]:
    """Load CurseForge-only exception list from curseforge_only.txt file."""
    exceptions_file = Path("curseforge_only.txt")
    exceptions = set()
    if exceptions_file.exists():
        with open(exceptions_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    exceptions.add(line)
    return exceptions


# Load CurseForge-only exceptions at startup
CURSEFORGE_ONLY_EXCEPTIONS = load_curseforge_only_exceptions()


def is_curseforge_only_exception(slug: str) -> bool:
    """Check if a CurseForge slug is in the exception list (CurseForge-only mods)."""
    return slug in CURSEFORGE_ONLY_EXCEPTIONS


def check_system_pakku() -> bool:
    """Check if pakku is installed on the command line."""
    # Try different ways to check for pakku
    commands_to_try = [
        ["pakku", "--version"],
        ["pakku", "-v"],
        ["pakku", "version"],
        ["pakku"],
    ]

    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )
            # Check if output contains pakku-related text
            output = (result.stdout + result.stderr).lower()
            if result.returncode == 0 or "pakku" in output:
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue

    return False


def check_java() -> bool:
    """Check if Java is installed and available."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def download_pakku() -> bool:
    """Download pakku.jar from GitHub releases."""
    print("Downloading pakku.jar from GitHub releases...")
    try:
        # Get latest release info
        response = requests.get(PAKKU_RELEASES_URL, timeout=10)
        response.raise_for_status()
        release_data = response.json()

        # Find the jar asset
        assets = release_data.get("assets", [])
        jar_asset = None
        for asset in assets:
            if asset.get("name", "").endswith(".jar"):
                jar_asset = asset
                break

        if not jar_asset:
            print("Error: Could not find jar file in latest release")
            return False

        # Download the jar
        download_url = jar_asset.get("browser_download_url")
        print(f"Downloading from: {download_url}")

        jar_response = requests.get(download_url, timeout=60)
        jar_response.raise_for_status()

        with open(PAKKU_JAR, "wb") as f:
            f.write(jar_response.content)

        debug_print(f"[OK] Successfully downloaded {PAKKU_JAR}")
        return True

    except Exception as e:
        print(f"Error downloading pakku.jar: {e}")
        return False


def ask_auto_run() -> bool:
    """Ask user if they want to automatically run commands."""
    print()
    print("=" * 60)
    print("Auto-run Options")
    print("=" * 60)
    print()
    print("Found mods that can be automatically added.")
    print("You can:")
    print("  1. Automatically run the commands (will auto-confirm prompts)")
    print("  2. Just display the commands for manual copy-paste")
    print()

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Invalid choice. Please enter 1 or 2.")


def run_pakku_rm(
    slug: str,
    use_system_pakku: bool = False,
    auto_confirm: bool = False,
) -> bool:
    """Run pakku rm command to remove a mod."""
    if use_system_pakku:
        cmd = ["pakku", "rm", slug]
    else:
        cmd = ["java", "-jar", str(PAKKU_JAR), "rm", slug]

    try:
        print(f"  Removing existing mod: {slug}")

        if auto_confirm:
            # Use communicate to send "y" immediately without blocking on readline
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Send "y\n" immediately and collect output
            stdout, _ = process.communicate(input="y\n", timeout=30)

            # Print the output
            for line in stdout.splitlines():
                print(f"    {line}")

            return process.returncode == 0
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0

    except Exception as e:
        print(f"  [X] Error removing mod: {e}")
        return False


def run_pakku_add(
    cf_slug: str,
    mr_slug: str,
    use_system_pakku: bool = False,
    auto_confirm: bool = False,
) -> tuple[bool, Optional[str]]:
    """Run pakku add prj command for a mod.
    Returns (success, existing_slug_to_remove) tuple.
    If existing_slug_to_remove is not None, that slug should be removed and the add retried.
    """
    if use_system_pakku:
        cmd = [
            "pakku",
            "add",
            "prj",
            "--cf",
            cf_slug,
            "--mr",
            mr_slug,
        ]
    else:
        cmd = [
            "java",
            "-jar",
            str(PAKKU_JAR),
            "add",
            "prj",
            "--cf",
            cf_slug,
            "--mr",
            mr_slug,
        ]

    try:
        print(f"  Running: pakku add prj --cf {cf_slug} --mr {mr_slug}")

        if auto_confirm:
            # Use Popen to handle interactive prompts with proper encoding
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            output_lines = []

            while True:
                if not process.stdout:
                    break
                try:
                    line = process.stdout.readline()
                except UnicodeDecodeError:
                    continue

                if not line:
                    if process.poll() is not None:
                        break
                    continue

                line_str = line.rstrip()
                print(f"    {line_str}")
                output_lines.append(line_str)

                # Check if pakku is asking for confirmation
                if "[y/N]:" in line_str or "[Y/n]:" in line_str or "?" in line_str:
                    if process.stdin:
                        process.stdin.write("y\n")
                        process.stdin.flush()

            return_code = process.wait()
            full_output = "\n".join(output_lines)

            # Debug: Show what we're checking
            debug_print("  [Debug] Checking full_output for 'already exists'...")
            debug_print(f"  [Debug] full_output preview: {full_output[:200]}...")
            debug_print(f"  [Debug] Return code: {return_code}")

            # Check for "already added" first, even if return code is 0 (pakku may auto-replace)
            # But skip if pakku already replaced it successfully
            if (
                "already added" in full_output.lower()
                and "replaced" not in full_output.lower()
            ):
                # Extract which slug is already added from output like "MOD {mr=terrablender} is already added"
                existing_slug = None
                for line in output_lines:
                    if "already added" in line.lower():
                        # Look for patterns like {mr=slug} or {cf=slug}
                        match = re.search(r"\{(?:mr|cf)=([^}]+)\}", line)
                        if match:
                            existing_slug = match.group(1)
                            break

                if existing_slug:
                    print(
                        f"  [Info] Mod already exists with slug '{existing_slug}' - needs removal and retry"
                    )
                    return False, existing_slug
                else:
                    print("  [Info] Mod already exists - needs removal and retry")
                    # Default to cf_slug if we can't parse the existing one
                    return False, cf_slug

            if return_code == 0 or "replaced" in full_output.lower():
                print("  [OK] Successfully added")
                return True, None
            else:
                print(f"  [X] Failed with exit code {return_code}")
                return False, None
        else:
            # Just run without auto-confirm
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Check for "already added" first, even if return code is 0
            # But skip if pakku already replaced it successfully
            if (
                "already added" in result.stderr.lower()
                and "replaced" not in result.stderr.lower()
            ):
                # Extract which slug is already added from stderr
                existing_slug = None
                match = re.search(r"\{(?:mr|cf)=([^}]+)\}", result.stderr)
                if match:
                    existing_slug = match.group(1)

                if existing_slug:
                    print(
                        f"  [Info] Mod already exists with slug '{existing_slug}' - needs removal and retry"
                    )
                    return False, existing_slug
                else:
                    print("  [Info] Mod already exists - needs removal and retry")
                    return False, cf_slug

            if result.returncode == 0:
                print("  [OK] Successfully added")
                return True, None
            else:
                print(f"  [X] Failed: {result.stderr.strip()}")
                return False, None

    except subprocess.TimeoutExpired:
        print("  [X] Command timed out")
        return False, None
    except Exception as e:
        print(f"  [X] Error: {e}")
        return False, None


def load_or_setup_cf_api_key() -> Optional[str]:
    """
    Load CurseForge API key from .env file or ask user to set it up.
    Returns the API key or None if user declines.
    """
    # Check if .env file exists and has the key
    if ENV_FILE.exists():
        debug_print(f"[Debug] Reading API key from {ENV_FILE}")
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("CURSEFORGE_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("\"'")
                    debug_print(
                        f"[Debug] Found key in .env (length: {len(key) if key else 0})"
                    )
                    debug_print(f"[Debug] Key preview: {key[:20] if key else 'N/A'}...")
                    if key:
                        return key
    else:
        debug_print(f"[Debug] .env file not found at {ENV_FILE.absolute()}")

    # Ask user if they want to provide the API key
    print("=" * 60)
    print("CurseForge API Setup")
    print("=" * 60)
    print("To search for mods on CurseForge, you need an API key.")
    print("You can get one from: https://console.curseforge.com/")
    print()
    print("Options:")
    print("  1. Enter your API key now (will be saved to .env)")
    print("  2. Skip CurseForge API (only Modrinth will be searched)")
    print()

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == "1":
            key = input("Enter your CurseForge API key: ").strip()
            if key:
                # Save to .env file
                with open(ENV_FILE, "w", encoding="utf-8") as f:
                    f.write(f"CURSEFORGE_API_KEY={key}\n")
                    f.write("USE_CURSEFORGE_API=true\n")
                print(f"\n[OK] API key saved to {ENV_FILE}\n")
                print("CurseForge API will be used for searches.")
                return key
            else:
                print("No key entered. Skipping CurseForge searches.\n")
                return None

        elif choice == "2":
            print("\nSkipping CurseForge API. Only Modrinth will be searched.\n")
            # Create .env with USE_CURSEFORGE_API=false to avoid asking again
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("# CurseForge API key not configured\n")
                f.write("USE_CURSEFORGE_API=false\n")
            return None

        else:
            print("Invalid choice. Please enter 1 or 2.")


def clean_search_query(query: str) -> str:
    """
    Clean search query by removing text in brackets and parentheses.
    E.g., "Cloth Config API (Fabric/Forge/NeoForge)" becomes "Cloth Config API"
    """
    import re

    # Remove text in parentheses () and brackets []
    cleaned = re.sub(r"\s*[\(\[].*?[\)\]]\s*", " ", query)
    # Trim whitespace
    cleaned = cleaned.strip()
    return cleaned


def search_modrinth(
    query: str, project_type: str, mc_versions: List[str], loaders: List[str]
) -> Optional[str]:
    """
    Search Modrinth for a mod using facets for better accuracy.
    First tries exact slug match, then falls back to search.
    Returns the slug of the best match or None if not found.
    """
    # Clean the query first
    query = clean_search_query(query)

    try:
        # First try exact slug match
        slug_url = f"{MODRINTH_API_URL}/project/{query}"
        debug_print(f"    [Debug] Trying exact slug match: {slug_url}")

        slug_response = requests.get(slug_url, timeout=10)
        if slug_response.status_code == 200:
            project_data = slug_response.json()
            # Check if the project supports the target Minecraft version
            project_versions = project_data.get("game_versions", [])
            if mc_versions:
                # Check if any target version is in the project's supported versions
                version_match = any(v in project_versions for v in mc_versions)
                if version_match:
                    debug_print(
                        f"    [Debug] Found exact slug match with version support: {project_data.get('slug')}"
                    )
                    return project_data.get("slug")
                else:
                    debug_print(
                        f"    [Debug] Exact slug found but doesn't support versions {mc_versions} (supports: {project_versions}), falling back to search"
                    )
            else:
                # No version check needed
                debug_print(
                    f"    [Debug] Found exact slug match: {project_data.get('slug')}"
                )
                return project_data.get("slug")
        elif slug_response.status_code == 404:
            debug_print(
                f"    [Debug] No exact slug match found, falling back to search"
            )
        else:
            debug_print(
                f"    [Debug] Slug lookup returned status {slug_response.status_code}"
            )

        # Build facets for search
        facets = []

        # Project type facet
        type_mapping = {
            "MOD": "mod",
            "MODPACK": "modpack",
            "RESOURCEPACK": "resourcepack",
            "SHADER": "shader",
        }
        mapped_type = type_mapping.get(project_type, "mod")
        facets.append(f"project_type:{mapped_type}")

        # Add version facets (OR logic within same array)
        if mc_versions:
            version_facets = [f"versions:{v}" for v in mc_versions]
            facets.extend(version_facets)
            debug_print(f"    [Debug] Searching Modrinth for versions: {mc_versions}")

        # Add loader facets - ensure neoforge is included
        if loaders:
            loader_facets = [f"categories:{loader}" for loader in loaders]
            facets.extend(loader_facets)
            debug_print(f"    [Debug] Searching Modrinth for loaders: {loaders}")
        else:
            # Default to neoforge if no loaders specified
            facets.append("categories:neoforge")
            debug_print(f"    [Debug] Defaulting to neoforge loader")

        url = f"{MODRINTH_API_URL}/search"
        params = {
            "query": query,
            "limit": 5,
            "facets": json.dumps([facets]),  # Nested array for AND logic
        }

        debug_print(f"    [Debug] Modrinth search params: {params}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        hits = data.get("hits", [])

        if not hits:
            debug_print(f"    [Debug] Modrinth search returned no results")
            return None

        # Check each hit to find one that supports the target version
        for hit in hits:
            found_slug = hit.get("slug")
            # Get project details to check supported versions
            try:
                project_url = f"{MODRINTH_API_URL}/project/{found_slug}"
                project_response = requests.get(project_url, timeout=10)
                if project_response.status_code == 200:
                    project_data = project_response.json()
                    project_versions = project_data.get("game_versions", [])
                    if mc_versions:
                        version_match = any(v in project_versions for v in mc_versions)
                        if version_match:
                            debug_print(
                                f"    [Debug] Modrinth search found with version support: {found_slug}"
                            )
                            return found_slug
                        else:
                            debug_print(
                                f"    [Debug] Found {found_slug} but doesn't support {mc_versions} (supports: {project_versions})"
                            )
                    else:
                        # No version check needed
                        debug_print(f"    [Debug] Modrinth search found: {found_slug}")
                        return found_slug
            except Exception as e:
                debug_print(
                    f"    [Debug] Error checking project details for {found_slug}: {e}"
                )

        debug_print(f"    [Debug] No search results support the target versions")
        return None

    except Exception as e:
        print(f"    [Modrinth search error: {e}]")
        return None


def slugify(text: str) -> str:
    """Convert text to slug format (lowercase, spaces to hyphens)."""
    # Replace spaces and underscores with hyphens
    slug = text.replace(" ", "-").replace("_", "-")
    # Remove special characters except hyphens
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    # Convert to lowercase and remove leading/trailing hyphens
    slug = slug.lower().strip("-")
    return slug


def check_mod_compatibility(
    mod_id: int,
    api_key: str,
    game_version: Optional[str] = None,
    mod_loader_type: Optional[int] = None,
) -> Tuple[bool, str, bool]:
    """
    Check mod details and report which modloaders it supports.
    Returns (is_found, message, has_fork_warning).
    """
    try:
        url = f"{CURSEFORGE_API_URL}/mods/{mod_id}"
        headers = {"Accept": "application/json", "x-api-key": api_key}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        mod = data.get("data", {})

        if not mod:
            return False, "Could not retrieve mod details", False

        latest_files_indexes = mod.get("latestFilesIndexes", [])

        # Divine which modloaders the project has
        modloaders = set()
        loader_type_ids = set()
        loader_names = {
            0: "Any",
            1: "Forge",
            2: "Cauldron",
            3: "LiteLoader",
            4: "Fabric",
            5: "Quilt",
            6: "NeoForge",
        }

        for index in latest_files_indexes:
            loader_type = index.get("modLoader")
            if loader_type is not None:
                loader_type_ids.add(loader_type)
                loader_name = loader_names.get(loader_type, f"Type {loader_type}")
                modloaders.add(loader_name)

        mod_name = mod.get("name", "Unknown")
        mod_slug = mod.get("slug", "Unknown")
        mod_url = f"https://www.curseforge.com/minecraft/mc-mods/{mod_slug}"

        if modloaders:
            debug_print(
                f"    [Debug] '{mod_name}' supports modloaders: {', '.join(sorted(modloaders))}"
            )
        else:
            debug_print(f"    [Debug] '{mod_name}' modloader information not available")

        # Check if requested modloader is supported
        has_fork_warning = False
        if mod_loader_type is not None and mod_loader_type not in loader_type_ids:
            requested_name = loader_names.get(
                mod_loader_type, f"Type {mod_loader_type}"
            )
            supported_list = ", ".join(sorted(modloaders)) if modloaders else "Unknown"
            print(
                f"    [!] Warning: '{mod_name}' does not support {requested_name} "
                f"(only: {supported_list}).\n"
                f"      You may need to find a fork or alternate listing for {requested_name}.\n"
                f"      Check: {mod_url}"
            )
            has_fork_warning = True

        # Always return True - we just want to divine what it has, not filter it out
        return True, f"Found: {mod_slug}", has_fork_warning

    except Exception as e:
        return False, f"Error checking mod details: {e}", False


def search_curseforge(
    query: str,
    api_key: str,
    game_version: Optional[str] = None,
    mod_loader_type: Optional[int] = None,
) -> Tuple[Optional[str], bool]:
    """
    Search CurseForge for a mod.
    Returns the slug of the best match or None if not found.
    """
    try:
        url = f"{CURSEFORGE_API_URL}/mods/search"
        headers = {"Accept": "application/json", "x-api-key": api_key}

        # Try searching by slug first (more exact match)
        slug_query = slugify(query)
        debug_print(f"    [Debug] Trying slug search with: '{slug_query}'")

        slug_params: Dict[str, Any] = {
            "gameId": 432,  # Minecraft
            "classId": 6,  # Mods only
            "slug": slug_query,
            "pageSize": 5,
        }

        response = requests.get(url, headers=headers, params=slug_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        mods = data.get("data", [])

        if mods:
            mod = mods[0]
            debug_print(f"    [Debug] Slug search found {len(mods)} result(s)")
            debug_print(
                f"    [Debug] Found: name='{mod.get('name')}', slug='{mod.get('slug')}'"
            )
            # Check compatibility
            is_compatible, message, has_fork_warning = check_mod_compatibility(
                mod.get("id"), api_key, game_version, mod_loader_type
            )
            if is_compatible:
                return mod.get("slug"), has_fork_warning
            else:
                print(message)
                return None, False

        # Fall back to general search if slug search fails
        debug_print(
            f"    [Debug] Slug search failed, trying general search for: '{query}'"
        )

        search_params: Dict[str, Any] = {
            "gameId": 432,  # Minecraft
            "classId": 6,  # Mods only
            "searchFilter": query,
            "pageSize": 10,
        }

        # Add version and modloader filters if available
        if game_version:
            search_params["gameVersion"] = game_version
            print(f"    [Debug] Adding gameVersion filter: {game_version}")

        if mod_loader_type is not None:
            search_params["modLoaderType"] = mod_loader_type
            print(f"    [Debug] Adding modLoaderType filter: {mod_loader_type}")

        debug_print(f"[Debug] Making request to: {url}")
        debug_print(f"[Debug] Params: {search_params}")
        debug_print(f"[Debug] API Key (first 20 chars): {api_key[:20]}...")
        response = requests.get(url, headers=headers, params=search_params, timeout=10)
        debug_print(f"[Debug] Response status: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        mods = data.get("data", [])

        # Debug: Show first 3 results (or 0 if empty)
        debug_print(f"    [Debug] General search returned {len(mods)} result(s)")
        if mods:
            has_fork_warning = False
            for i, mod in enumerate(mods[:3], 1):
                mod_name = mod.get("name", "N/A")
                mod_slug = mod.get("slug", "N/A")
                mod_id = mod.get("id", "N/A")
                debug_print(
                    f"    [Debug] Result {i}: name='{mod_name}', slug='{mod_slug}', id={mod_id}"
                )
                # Check compatibility for the first result
                if i == 1:
                    is_compatible, message, has_fork_warning = check_mod_compatibility(
                        mod_id, api_key, game_version, mod_loader_type
                    )
                    if not is_compatible:
                        print(message)
                        return None, False
                    # Return the slug of the first (best) result
                    return mods[0].get("slug"), has_fork_warning
            # Fallback return if loop completes without returning (shouldn't happen)
            return None, False
        else:
            # Debug: Show raw response when no mods found
            debug_print(f"    [Debug] Raw response keys: {list(data.keys())}")
            return None, False

    except Exception as e:
        print(f"    [CurseForge search error: {e}]")
        return None, False


def get_loader_mapping(loader: str) -> Tuple[Optional[int], str]:
    """
    Map pakku loader names to CurseForge modLoaderType and Modrinth categories.
    Returns (curseforge_type, modrinth_category)
    """
    mapping = {
        "neoforge": (6, "neoforge"),
        "forge": (1, "forge"),
        "fabric": (4, "fabric"),
        "quilt": (5, "quilt"),
        "liteloader": (2, "liteloader"),
        "rift": (4, "rift"),  # Rift maps to fabric-ish
        "modloader": (6, "modloader"),  # Risugami's ModLoader
    }
    return mapping.get(loader.lower(), (None, loader.lower()))


def extract_lock_info(data: Dict) -> Tuple[List[str], List[str]]:
    """
    Extract MC versions and loaders from pakku-lock.json.
    Returns (mc_versions, loaders)
    """
    mc_versions = data.get("mc_versions", [])
    loaders_data = data.get("loaders", {})
    loaders = list(loaders_data.keys()) if loaders_data else []
    return mc_versions, loaders


def check_mod_platforms(
    filepath: Path, cf_api_key: Optional[str]
) -> Tuple[List[Dict], List[str], List[str]]:
    """Check that all projects have both CurseForge and Modrinth entries."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    projects = data.get("projects", [])
    mc_versions, loaders = extract_lock_info(data)

    incomplete_mods = []

    for project in projects:
        # Get identifier for reporting
        name_data = project.get("name", {})
        slug_data = project.get("slug", {})
        id_data = project.get("id", {})
        project_type = project.get("type", "MOD")

        # Determine display name (prefer Modrinth, fallback to CurseForge or ID)
        display_name = (
            name_data.get("modrinth")
            or name_data.get("curseforge")
            or slug_data.get("modrinth")
            or slug_data.get("curseforge")
            or project.get("pakku_id", "Unknown")
        )

        missing_fields = []

        # Check slug
        if not slug_data.get("curseforge"):
            missing_fields.append("slug.curseforge")
        if not slug_data.get("modrinth"):
            missing_fields.append("slug.modrinth")

        # Check name
        if not name_data.get("curseforge"):
            missing_fields.append("name.curseforge")
        if not name_data.get("modrinth"):
            missing_fields.append("name.modrinth")

        # Check id
        if not id_data.get("curseforge"):
            missing_fields.append("id.curseforge")
        if not id_data.get("modrinth"):
            missing_fields.append("id.modrinth")

        # Check files array
        files = project.get("files", [])
        has_cf_file = any(f.get("type") == "curseforge" for f in files)
        has_mr_file = any(f.get("type") == "modrinth" for f in files)

        if not has_cf_file:
            missing_fields.append("files.curseforge")
        if not has_mr_file:
            missing_fields.append("files.modrinth")

        if missing_fields:
            # Determine which platform is missing
            platforms = set()
            for field in missing_fields:
                if "curseforge" in field:
                    platforms.add("CurseForge")
                elif "modrinth" in field:
                    platforms.add("Modrinth")

            # Get available slugs and names for searching
            cf_slug = slug_data.get("curseforge")
            mr_slug = slug_data.get("modrinth")
            cf_name = name_data.get("curseforge")
            mr_name = name_data.get("modrinth")

            # Check if this mod needs re-addition (has both slugs but missing files)
            needs_readdition = (
                cf_slug and mr_slug and (not has_cf_file or not has_mr_file)
            )

            incomplete_mods.append(
                {
                    "name": display_name,
                    "pakku_id": project.get("pakku_id", "N/A"),
                    "missing_fields": missing_fields,
                    "missing_platforms": list(platforms),
                    "cf_slug": cf_slug,
                    "mr_slug": mr_slug,
                    "cf_name": cf_name,
                    "mr_name": mr_name,
                    "project_type": project_type,
                    "needs_readdition": needs_readdition,
                }
            )

    return incomplete_mods, mc_versions, loaders


def main():
    filepath = Path("./pakku-lock.json")

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    # Setup CurseForge API key
    cf_api_key = load_or_setup_cf_api_key()

    # Check mods
    incomplete, mc_versions, loaders = check_mod_platforms(filepath, cf_api_key)

    if not incomplete:
        print("=" * 60)
        print("[OK] All mods have both CurseForge and Modrinth counterparts")
        print("=" * 60)
        return 0

    print("=" * 60)
    print(f"Found {len(incomplete)} mod(s) missing platform counterparts")
    print("=" * 60)
    print()

    # Get primary MC version and loader for CurseForge search
    primary_mc_version = mc_versions[0] if mc_versions else None
    primary_loader = loaders[0] if loaders else None
    cf_loader_type, _ = (
        get_loader_mapping(primary_loader) if primary_loader else (None, "")
    )

    # First pass: Show summary of all mods with issues
    print("Summary of mods missing platform counterparts:\n")
    for i, mod in enumerate(incomplete, 1):
        status = (
            f"Missing {mod['missing_platforms'][0]} entry."
            if len(mod["missing_platforms"]) == 1
            else f"Missing: {', '.join(mod['missing_platforms'])}"
        )
        print(f"{i}. {mod['name']} - ID: {mod['pakku_id']} - {status}")

    print()

    # Second pass: Search for missing platforms and collect commands
    ready_commands = []  # Commands with all slugs found
    manual_commands = []  # Commands that need manual slug lookup
    fork_warnings = []  # Mods that have fork warnings (not auto-added)

    for mod in incomplete:
        print(f"Processing: {mod['name']}")

        # Check if this mod needs re-addition (has both slugs but missing files)
        if mod.get("needs_readdition"):
            cf_slug = mod.get("cf_slug")
            mr_slug = mod.get("mr_slug")
            print("  [!] Mod has both slugs but missing files - needs re-addition")
            print(f"  [Info] Using existing CurseForge slug: {cf_slug}")
            print(f"  [Info] Using existing Modrinth slug: {mr_slug}")

            # Build command with existing slugs
            cmd_parts = ["pakku add prj"]
            cmd_parts.append(f'--cf "{cf_slug}"')
            cmd_parts.append(f'--mr "{mr_slug}"')
            ready_commands.append((mod["name"], " ".join(cmd_parts)))
            print("  [OK] Added to ready commands for re-addition")
            print()
            continue

        mod_has_fork_warning = False

        # Get current slugs and names
        cf_slug = mod.get("cf_slug")
        mr_slug = mod.get("mr_slug")
        cf_name = mod.get("cf_name")
        mr_name = mod.get("mr_name")
        project_type = mod.get("project_type", "MOD")

        # Search for missing platform
        searched_slug = None
        search_platform = None

        if not mr_slug and (cf_name or cf_slug):
            # Check if this is a CurseForge-only exception
            if cf_slug and is_curseforge_only_exception(cf_slug):
                print(
                    f"  [!] CurseForge-only exception: '{cf_slug}' - skipping Modrinth search"
                )
                print(f"  [Info] This mod should be handled manually")
                manual_commands.append((mod["name"], f"# CurseForge-only: {cf_slug}"))
                print()
                continue

            # Try exact slug match first, then fall back to name search
            if cf_slug:
                print(f"  Trying exact Modrinth match for slug: '{cf_slug}'...")
                exact_match = search_modrinth(
                    query=cf_slug,
                    project_type=project_type,
                    mc_versions=mc_versions,
                    loaders=loaders,
                )
                if exact_match:
                    # Verify the result matches what we're looking for
                    if (
                        exact_match.lower() == cf_slug.lower()
                        or exact_match.lower().replace("-", "")
                        == cf_slug.lower().replace("-", "")
                    ):
                        searched_slug = exact_match
                        search_platform = "modrinth"
                        print(f"  [OK] Found exact match on Modrinth: {searched_slug}")
                        time.sleep(0.5)  # Rate limiting
                    else:
                        print(
                            f"  [!] Found '{exact_match}' but it doesn't match '{cf_slug}', treating as not found"
                        )
                        # Fall back to name-based search
                        if cf_name:
                            print(f"  Searching Modrinth for: '{cf_name}'...")
                            debug_print(
                                f"    Filters: versions={mc_versions}, loaders={loaders}, type={project_type}"
                            )
                            searched_slug = search_modrinth(
                                query=cf_name,
                                project_type=project_type,
                                mc_versions=mc_versions,
                                loaders=loaders,
                            )
                            search_platform = "modrinth"
                            if searched_slug:
                                print(f"  [OK] Found on Modrinth: {searched_slug}")
                            else:
                                print("  [X] Not found on Modrinth")
                        else:
                            print(
                                "  [X] No exact match and no name available for search"
                            )
                        time.sleep(0.5)  # Rate limiting
                else:
                    # Fall back to name-based search
                    if cf_name:
                        print(f"  Searching Modrinth for: '{cf_name}'...")
                        debug_print(
                            f"    Filters: versions={mc_versions}, loaders={loaders}, type={project_type}"
                        )
                        searched_slug = search_modrinth(
                            query=cf_name,
                            project_type=project_type,
                            mc_versions=mc_versions,
                            loaders=loaders,
                        )
                        search_platform = "modrinth"
                        if searched_slug:
                            print(f"  [OK] Found on Modrinth: {searched_slug}")
                        else:
                            print("  [X] Not found on Modrinth")
                    else:
                        print("  [X] No exact match and no name available for search")
                    time.sleep(0.5)  # Rate limiting
            elif cf_name:
                # No slug available, use name
                print(f"  Searching Modrinth for: '{cf_name}'...")
                debug_print(
                    f"    Filters: versions={mc_versions}, loaders={loaders}, type={project_type}"
                )
                searched_slug = search_modrinth(
                    query=cf_name,
                    project_type=project_type,
                    mc_versions=mc_versions,
                    loaders=loaders,
                )
                search_platform = "modrinth"
                if searched_slug:
                    print(f"  [OK] Found on Modrinth: {searched_slug}")
                else:
                    print("  [X] Not found on Modrinth")
                time.sleep(0.5)  # Rate limiting
            else:
                print("  Cannot search Modrinth: no name or slug available")
        elif not cf_slug and (mr_name or mr_slug) and use_curseforge_api():
            # Try exact slug match first, then fall back to name search
            if mr_slug:
                print(f"  Trying exact CurseForge match for slug: '{mr_slug}'...")
                # Ensure api_key is not None
                assert cf_api_key is not None, (
                    "API key should not be None when use_curseforge_api() is True"
                )
                exact_match = search_curseforge(
                    query=mr_slug,
                    api_key=cf_api_key,
                    game_version=primary_mc_version,
                    mod_loader_type=cf_loader_type,
                )
                if isinstance(exact_match, tuple):
                    exact_slug, exact_fork = (
                        exact_match[0],
                        exact_match[1] if len(exact_match) > 1 else False,
                    )
                else:
                    exact_slug, exact_fork = exact_match, False

                if exact_slug:
                    # Verify the result matches what we're looking for
                    if (
                        exact_slug.lower() == mr_slug.lower()
                        or exact_slug.lower().replace("-", "")
                        == mr_slug.lower().replace("-", "")
                    ):
                        searched_slug = exact_slug
                        mod_has_fork_warning = exact_fork
                        search_platform = "curseforge"
                        print(
                            f"  [OK] Found exact match on CurseForge: {searched_slug}"
                        )
                        if mod_has_fork_warning:
                            print(
                                f"  [!] Note: {mod['name']} has fork warning - will not auto-add"
                            )
                    else:
                        print(
                            f"  [!] Found '{exact_slug}' but it doesn't match '{mr_slug}', treating as not found"
                        )
                        # Fall back to name-based search
                        if mr_name:
                            print(f"  Searching CurseForge for: '{mr_name}'...")
                            if primary_mc_version:
                                debug_print(
                                    f"    Filters: version={primary_mc_version}, loader_type={cf_loader_type}"
                                )

                            result = search_curseforge(
                                query=mr_name,
                                api_key=cf_api_key,
                                game_version=primary_mc_version,
                                mod_loader_type=cf_loader_type,
                            )
                            if isinstance(result, tuple):
                                searched_slug, mod_has_fork_warning = result
                            else:
                                searched_slug = result
                                mod_has_fork_warning = False
                            search_platform = "curseforge"

                            if searched_slug:
                                print(f"  [OK] Found on CurseForge: {searched_slug}")
                                if mod_has_fork_warning:
                                    print(
                                        f"  [!] Note: {mod['name']} has fork warning - will not auto-add"
                                    )
                            else:
                                print("  [X] Not found on CurseForge")
                        else:
                            print(
                                "  [X] No exact match and no name available for search"
                            )
                else:
                    # Fall back to name-based search
                    if mr_name:
                        print(f"  Searching CurseForge for: '{mr_name}'...")
                        if primary_mc_version:
                            debug_print(
                                f"    Filters: version={primary_mc_version}, loader_type={cf_loader_type}"
                            )

                        result = search_curseforge(
                            query=mr_name,
                            api_key=cf_api_key,
                            game_version=primary_mc_version,
                            mod_loader_type=cf_loader_type,
                        )
                        if isinstance(result, tuple):
                            searched_slug, mod_has_fork_warning = result
                        else:
                            searched_slug = result
                            mod_has_fork_warning = False
                        search_platform = "curseforge"

                        if searched_slug:
                            print(f"  [OK] Found on CurseForge: {searched_slug}")
                            if mod_has_fork_warning:
                                print(
                                    f"  [!] Note: {mod['name']} has fork warning - will not auto-add"
                                )
                        else:
                            print("  [X] Not found on CurseForge")
                    else:
                        print("  [X] No exact match and no name available for search")
            elif mr_name:
                # No slug available, use name
                print(f"  Searching CurseForge for: '{mr_name}'...")
                if primary_mc_version:
                    debug_print(
                        f"    Filters: version={primary_mc_version}, loader_type={cf_loader_type}"
                    )

                # Ensure api_key is not None
                assert cf_api_key is not None, (
                    "API key should not be None when use_curseforge_api() is True"
                )
                result = search_curseforge(
                    query=mr_name,
                    api_key=cf_api_key,
                    game_version=primary_mc_version,
                    mod_loader_type=cf_loader_type,
                )
                if isinstance(result, tuple):
                    searched_slug, mod_has_fork_warning = result
                else:
                    searched_slug = result
                    mod_has_fork_warning = False
                search_platform = "curseforge"

                if searched_slug:
                    print(f"  [OK] Found on CurseForge: {searched_slug}")
                    if mod_has_fork_warning:
                        print(
                            f"  [!] Note: {mod['name']} has fork warning - will not auto-add"
                        )
                else:
                    print("  [X] Not found on CurseForge")
            else:
                print("  Cannot search CurseForge: no name or slug available")
        else:
            print("  No search possible: missing required information")

        # Determine final slugs for command
        final_cf_slug = cf_slug or (
            searched_slug if search_platform == "curseforge" else "<curseforge_slug>"
        )
        final_mr_slug = mr_slug or (
            searched_slug if search_platform == "modrinth" else "<modrinth_slug>"
        )

        # Debug output for slugs
        debug_print(f"    [Debug] cf_slug from mod: {cf_slug}")
        debug_print(f"    [Debug] mr_slug from mod: {mr_slug}")
        debug_print(f"    [Debug] search_platform: {search_platform}")
        debug_print(f"    [Debug] searched_slug: {searched_slug}")
        debug_print(f"    [Debug] final_cf_slug: {final_cf_slug}")
        debug_print(f"    [Debug] final_mr_slug: {final_mr_slug}")

        # Build command
        cmd_parts = ["pakku add prj"]
        has_placeholder = False

        if final_cf_slug and final_cf_slug != "<curseforge_slug>":
            cmd_parts.append(f'--cf "{final_cf_slug}"')
        else:
            cmd_parts.append('--cf "<curseforge_slug>"')
            has_placeholder = True

        if final_mr_slug and final_mr_slug != "<modrinth_slug>":
            cmd_parts.append(f'--mr "{final_mr_slug}"')
        else:
            cmd_parts.append('--mr "<modrinth_slug>"')
            has_placeholder = True

        command = " ".join(cmd_parts)
        if has_placeholder:
            manual_commands.append((mod["name"], command))
        elif mod_has_fork_warning:
            fork_warnings.append(
                (mod["name"], command, "Mod may need fork for your modloader")
            )
        else:
            ready_commands.append((mod["name"], command))
        print()

    # Check for pakku availability (system or jar)
    system_pakku = check_system_pakku()
    java_available = check_java()
    pakku_available = False
    use_system_pakku = False

    # Ask user if they want to auto-run commands
    auto_run = False
    if ready_commands and (system_pakku or java_available):
        auto_run = ask_auto_run()

        if auto_run:
            if system_pakku:
                print("=" * 60)
                print("Using system-installed pakku")
                print("=" * 60)
                pakku_available = True
                use_system_pakku = True
                print()
            elif java_available:
                print("=" * 60)
                print("Setting up pakku.jar for automatic mod addition...")
                print("=" * 60)
                if PAKKU_JAR.exists():
                    print(f"Found existing {PAKKU_JAR}")
                    pakku_available = True
                else:
                    pakku_available = download_pakku()
                if not pakku_available:
                    print("Warning: Could not set up pakku, will show commands instead")
                print()

    # Auto-add mods with both slugs found
    auto_added = []
    failed_to_add = []

    if auto_run and ready_commands and pakku_available:
        print("=" * 60)
        print("Automatically adding mods with found slugs...")
        print("=" * 60)
        print()

        for mod_name, cmd_str in ready_commands:
            # Parse the command to extract slugs
            # Format: pakku add prj --cf "slug" --mr "slug"
            parts = cmd_str.split()
            cf_idx = parts.index("--cf") if "--cf" in parts else -1
            mr_idx = parts.index("--mr") if "--mr" in parts else -1

            if cf_idx != -1 and mr_idx != -1:
                cf_slug = parts[cf_idx + 1].strip('"')
                mr_slug = parts[mr_idx + 1].strip('"')

                print(f"Adding: {mod_name}")
                success, existing_slug_to_remove = run_pakku_add(
                    cf_slug, mr_slug, use_system_pakku, auto_confirm=True
                )

                debug_print(
                    f"  [Debug] success={success}, existing_slug_to_remove={existing_slug_to_remove}"
                )

                if success:
                    auto_added.append(mod_name)
                elif existing_slug_to_remove:
                    # Remove the existing mod using the slug we extracted from output
                    if run_pakku_rm(
                        existing_slug_to_remove, use_system_pakku, auto_confirm=True
                    ):
                        # Retry the add
                        print("  Retrying add after removal...")
                        success, _ = run_pakku_add(
                            cf_slug, mr_slug, use_system_pakku, auto_confirm=True
                        )
                        if success:
                            auto_added.append(mod_name)
                        else:
                            failed_to_add.append((mod_name, cmd_str))
                    else:
                        failed_to_add.append((mod_name, cmd_str))
                else:
                    failed_to_add.append((mod_name, cmd_str))
                print()

        print()

    # Print summary of results
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print()

    if auto_added:
        print(f"[OK] Automatically added {len(auto_added)} mod(s):")
        for name in auto_added:
            print(f"  - {name}")
        print()

    if failed_to_add:
        print(f"[X] Failed to add {len(failed_to_add)} mod(s):")
        for name, _ in failed_to_add:
            print(f"  - {name}")
        print()

    if fork_warnings:
        print(f"[!] {len(fork_warnings)} mod(s) need fork/alternate listing:")
        print("-" * 40)
        for mod_name, cmd, reason in fork_warnings:
            print(f"# {mod_name}")
            print(f"  Reason: {reason}")
            print(f"  Command: {cmd}")
        print()

    # Show commands that couldn't be auto-added
    # Note: fork_warnings are NOT included here - they require manual investigation
    # and are shown separately in their own section
    commands_to_show = []
    if failed_to_add:
        commands_to_show.extend([cmd for _, cmd in failed_to_add])
    if not (java_available and pakku_available):
        commands_to_show.extend([cmd for _, cmd in ready_commands])

    if commands_to_show:
        print("Commands to run manually:")
        print("-" * 40)
        for cmd in commands_to_show:
            print(cmd)
        print()

    if manual_commands:
        print("Need manual slug lookup:")
        print("-" * 40)
        for mod_name, cmd in manual_commands:
            print(f"# {mod_name}")
            print(cmd)
        print()
        print("To find the missing slugs:")
        print("  - Go to the mod's CurseForge or Modrinth page")
        print("  - The slug is the last part of the URL")
        print("    Example: https://modrinth.com/mod/alexs-mobs")
        print("             The slug is: alexs-mobs")
        print("  - Replace <curseforge_slug> or <modrinth_slug> with the actual slug")
        print()

    if not java_available and not system_pakku:
        print("Note: Java not found. Install Java to enable automatic mod addition.")
        print()

    if auto_added and not manual_commands and not failed_to_add and not fork_warnings:
        print("[OK] All mods have been successfully added!")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
