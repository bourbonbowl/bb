# bb
> This package fetches, compiles, and updates datasets used to power bourbon-bowl.com.

## Configuration
### Required for each code change
- `setup.py`
    - update `version` for each code change.
    - this will force local and gcp cloud function packages to be reinstalled.
- GCP Cloud Function: `gcf-bbUpdate`
    - confirm `version` has been updated in `setup.py`
    - update commit hash for repo url in `requirements.txt`.
        - ensures most recent code changes are referenced.
        - Example: update `402f8ac717c0718e73cbc334dd0973c91278191c` of `git+https://github.com/bourbonbowl/bb.git@402f8ac717c0718e73cbc334dd0973c91278191c` with new commit hash.
        - Obtain commit hash via github UI or with the following terminal function:
            ```text
                git rev-parse HEAD
            ```

---

### Required less frequently
- `bb/config.py`
    - update `current_league_year` as needed.
    - update `bucket` (gcp bucket id) as needed. 
- `_league_info.json`
    - add new entry for each new league year.
    - key can be found via the league url like `https://sleeper.com/leagues/1048315700445646848/`.
    - draft can be found via draft room url for league like `https://sleeper.com/draft/nfl/1048315700445646849`.
    - set `archived` to true for past years.
    - example:

        ```json
            "1048315700445646848": {
                "archived": false,
                "year": "2024",
                "draft_id": "1048315700445646849"
            }
        ```
---

### Other
- `_url_prefix.json`
    - updates only necessary if sleeper API changes.
- `_url_suffix.json`
    - updates only necessary if sleeper API changes.

---

## Update Process
1. Cloud Scheduler `bb-updater` send Pub/Sub message:
    - Scheduled to run every day at 10AM, 1PM, 3PM, and 8PM EST 
    - cron: `0 10,13,16,20 * * * (America/New_York)`
1. Cloud Function `gfc-bbUpdate` is triggered by `bb-updater` Pub/Sub message.
1. `gcf-bbUpdate` imports `bb` repo and calls functions:
    - `players.update_db()`
    - `users.update_db()`
    - `rosters.update_db()`
    - `drafts.update_db()`
    - `transactions.update_db()`
    - `_post.go()`
        - calls `_compile.bb_summary_output()` function.
        - calls `_compile.faab_flow()` function.
        - updates GCP Storage Bucket.
1. bourbon-bowl.com front end pulls data from GCP Storage Bucket.

---

## Resources
[Sleeper API Docs](https://docs.sleeper.com/)