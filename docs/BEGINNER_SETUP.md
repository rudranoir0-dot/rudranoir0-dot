# Living Realm setup

## What the files do

- `project-registry.json` stores your registered projects, districts, levels, and statuses.
- `scripts/build_realm.py` validates the registry, draws the SVG, and refreshes the README project table.
- `.github/workflows/update-realm.yml` runs the generator after configured events.
- `assets/realm.svg` is generated artwork. Do not edit it by hand.

## First run

1. Open the repository Settings → Actions → General.
2. Under Workflow permissions, enable read and write permissions so the workflow can commit generated output.
3. Open Actions → Update the Living Realm → Run workflow.
4. Check the run logs. The generator should create the SVG and update the project table.

## How growth works

A registered project is represented by a building. Level ranges from 1 to 5. A connected repository can send a `project_released` event when it publishes a release; the matching registered building rises one level, capped at level 5. Releases do not automatically mark a project completed. Keep project status accurate in the registry.

## Connect another repository

Follow `CONNECTING_PROJECTS.md`. Each repository you want to connect needs a repository secret containing a token with permission to dispatch an event to this realm repository. Never commit tokens to source files.
