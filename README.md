# Zotero Digest

A small Python tool that uses a Zotero collection as an interest profile, filters recent arXiv papers by your keywords, ranks them against the Zotero profile, and sends a daily email digest.

## Repository contents

- `src/zotero_digest/main.py` — CLI entrypoint
- `.github/workflows/daily.yml` — scheduled GitHub Actions workflow
- `.env.example` — example local/GitHub secret values
- `config.example.json` — optional structured config for `APP_CONFIG_JSON`

## Required configuration

Set these environment variables locally or as GitHub Actions secrets:

- `ZOTERO_USER_ID`
- `ZOTERO_API_KEY`
- `ZOTERO_COLLECTION_KEY`
- `KEYWORDS` — comma-separated keywords
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO` — comma-separated recipients
- `ARXIV_CATEGORIES` — optional, comma-separated arXiv categories like `cs.LG,cs.AI`
- `MAX_RESULTS` — optional, default `10`
- `LOOKBACK_HOURS` — optional, default `24`
- `STATE_PATH` — optional, default `.state/state.json`
- `REQUEST_TIMEOUT` — optional, default `30`
- `APP_CONFIG_JSON` — optional JSON override for structured config

## GitHub setup

1. Create a new GitHub repository and upload this project.
2. Open **Settings → Secrets and variables → Actions**.
3. Add the required secrets from `.env.example`.
4. If you want structured config, paste `config.example.json` content into a single secret named `APP_CONFIG_JSON`.
5. Push to your default branch.
6. Open the **Actions** tab and manually run `Daily digest` once with `workflow_dispatch`.

## Local usage

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e . pytest
export $(grep -v '^#' .env | xargs)
python -m zotero_digest.main --dry-run
pytest
```

If you do not want to create a local `.env`, you can export the variables manually.

`--dry-run` prints the ranked candidates without sending email, so you can validate your Zotero collection and keywords before enabling SMTP delivery.

## GitHub Actions

The workflow in `.github/workflows/daily.yml` runs once per day and can also be started manually with `workflow_dispatch`.

After each successful run it commits `.state/state.json` back to the repository so previously sent papers are not mailed again.

If you want a different delivery time, edit the cron expression in `.github/workflows/daily.yml`.

## First-run checklist

- Confirm the Zotero API key can read the target collection.
- Start with a narrow `ARXIV_CATEGORIES` list so the first run is easy to inspect.
- Run one `workflow_dispatch` job before relying on the daily schedule.
- Check the email formatting and whether the matched keywords look sensible.
- Tune `KEYWORDS`, `MAX_RESULTS`, and categories after the first digest.
