# Rename the default branch to main while retaining the container tag

- **Status:** Valid
- **Status date:** 2026-11-28
- **Decision date:** 2026-11-28
- **Decided by:** Sascha Trebbin (maintainer)
- **Related issue:** [#35 — Rename the default branch from master to main](https://github.com/saschatrebbin/simple-servicetag-generator/issues/35)

## Context and question

The repository's default branch was named `master` when the decision was made. Its name differs from the naming used in the maintainer's other repositories. The publishing workflow derives its image tag from the branch name and has published the image as `ghcr.io/saschatrebbin/simple-servicetag-generator:master`.

Renaming the branch must not silently leave existing users of that image tag with an out-of-date image. The wider question of test and production image tags is being considered separately in [issue #36](https://github.com/saschatrebbin/simple-servicetag-generator/issues/36).

## Options considered

### Keep publishing the `:master` image tag temporarily

- **Description:** Rename the default Git branch to `main` but explicitly publish new images from it under the existing `:master` tag.
- **Outcome:** Chosen as an interim solution.
- **Reasons:** Existing users can continue receiving updated images under the same tag while the broader tagging approach is considered in issue #36.

### Publish both `:master` and `:main`

- **Description:** Publish the same image under both tags, allowing users to migrate to `:main`.
- **Outcome:** Not chosen for this transition.
- **Reasons:** The long-term production and test tags are still to be decided in issue #36.

### Publish only `:main`

- **Description:** Adopt the new branch name as the image tag and stop updating `:master`.
- **Outcome:** Not chosen.
- **Reasons:** Existing deployments using `:master` would remain on the last image under that tag until their configuration was changed.

## Decision

Rename the default branch on GitHub from `master` to `main`. Keep the `development` branch and its test-only workflow. Prepare the image workflow to support both default-branch names during the transition, then restrict it to `main` after the rename.

Until a later decision is made in issue #36, explicitly publish the production image under the existing `:master` tag even when the source branch is `main`. The tag is independent of the Git branch name. Issue #35 tracks the implementation and verification; this decision record does not by itself imply that the rename has already happened.

## Rationale

The new branch name aligns this repository with the maintainer's other repositories. Keeping the image tag temporarily avoids requiring a simultaneous deployment migration and allows the wider image-tagging question to be decided separately.

## Consequences

- The GitHub default branch and current documentation will use `main` once the migration is complete. Existing local clones and external branch references may need updating.
- The published `:master` image tag continues to receive updates despite no longer matching the default branch name.
- The temporary period in which the workflow accepts both branch names must end after the rename.
- Pull-request tests, image verification, and publication need to be checked after the transition. Successful publication is distinct from updating a deployed container.

## Relationship to previous decisions

No earlier decision record is superseded. The [development test workflow decision](0002-development-test-workflow.md) continues to apply; its references to `master` describe the situation at the time.

## Additional references

- [Test and production image tags](https://github.com/saschatrebbin/simple-servicetag-generator/issues/36)
- [Architecture overview](../architecture.md)
- [GitHub: renaming a branch](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/renaming-a-branch)
