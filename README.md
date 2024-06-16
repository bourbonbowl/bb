# bbUpdate
> This package fetches, compiles, and updates datasets used to power bourbon-bowl.com.

## Configuration
### Required For Each Code Change To bbUpdate Module
- `setup.py`
    - update `version` for each code change.
    - this will force local and gcp cloud function packages to be reinstalled.
- GCP Cloud Function: `name tbd`
    - confirm `version` has been updated in `setup.py`
    - update commit hash at end of repo in Cloud Function `requirements.txt`.
        - this will ensure the most recent code changes are referenced by gcp cloud function.
        - Example: update `402f8ac717c0718e73cbc334dd0973c91278191c` of `git+https://github.com/bourbonbowl/bb.git@402f8ac717c0718e73cbc334dd0973c91278191c` with new commit hash.
        - Obtain commit hash via github UI or with the following terminal function:
            ```text
                git rev-parse HEAD
            ```

---

### Required Less Frequently
- `bbUpdate/config.py`
    - update `current_league_year` as needed.
    - update `bucket` (gcp bucket id) as needed. 
- `_league_info.json`
    - add new entry for each new league year.
    - key can be found via the league url like `https://sleeper.com/leagues/1048315700445646848/`.
    - draft can be found via draft room url for league like `https://sleeper.com/draft/nfl/1048315700445646849`.
    - set `archived` to true for past years.
    - example entry:

        ```json
            "1048315700445646848": {
                "archived": false,
                "year": "2024",
                "draft_id": "1048315700445646849"
            }
        ```
---

### Required Infrequently
- `_url_prefix.json`
    - updates only necessary if sleeper API changes.
- `_url_suffix.json`
    - updates only necessary if sleeper API changes.

---

## Overview
1. Cloud Scheduler `bb-updater` initiates Cloud Function `gfc-bbUpdate`.
2. `gcf-bbUpdate` imports `bb` repo.
3. `gcf-bbUpdate` calls `fetch_` and `data_post` `go()` functions. 
4. `data_post.go()` calls `data_compile.go()` function.
5. `data_post.go()` updates GCP Storage Bucket.
6. bourbon-bowl.com front end pulls data from GCP Storage Bucket.

---

## Functions

## Resources
[Sleeper API Docs](https://docs.sleeper.com/)