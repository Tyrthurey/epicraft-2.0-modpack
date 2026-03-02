# Epicraft 2.0 Modpack

Pakku is used to set things up.

Use `python check_mods.py pakku-lock.json` to make sure any mods added are in both curseforge and modrinth.

## GitHub Action Setup

### 1. Cloudflare R2 Setup

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → R2
2. Create a bucket (e.g., `epicraft-modpack`)
3. Create an API token:
   - R2 → Manage API Tokens → Create API Token
   - Select **Object Read & Write** permissions
   - Save the **Access Key ID** and **Secret Access Key**
4. Note your **Account ID** from the R2 dashboard sidebar
5. Your endpoint will be: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`

### 2. GitHub Repository Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|--------|-------|
| `R2_ACCESS_KEY_ID` | Cloudflare R2 API token Access Key ID |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 API token Secret Access Key |
| `R2_BUCKET` | Your bucket name |
| `R2_ENDPOINT` | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |
| `CURSEFORGE_API_KEY` | From [CurseForge API Keys](https://console.curseforge.com/?#/api-keys) |

### 3. Trigger the Workflow

1. Go to **Releases** → **Draft a new release**
2. Create a tag (e.g., `v1.0.0`)
3. Add release notes (becomes the changelog)
4. **Publish release**

The workflow will:
- Export the modpack via Pakku
- Import to Packwiz format
- Sync to your R2 bucket root (deleting old files)
- Upload `.mrpack` and `.zip` to the GitHub Release