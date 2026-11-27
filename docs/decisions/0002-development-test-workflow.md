# Run a separate test workflow for development

- **Status:** Valid
- **Status date:** 2026-11-27
- **Decision date:** 2026-11-27
- **Decided by:** Sascha Trebbin (maintainer)
- **Related issue:** [#28 — Test workflow for the development branch](https://github.com/saschatrebbin/simple-servicetag-generator/issues/28)

## Context and question

The new `APP_DEBUG` regression tests and later tests need an easy, repeatable way to run together on `development`. Tests must remain usable locally, including individually. The existing workflow targets pull requests to `master` and pushes to `master`, and includes image build or publication steps. The initial development test run must be possible without changing `master` and must run tests only.

## Options considered

### 1. Separate development test workflow

- **Description:** Run all Python tests on pushes to `development`, permit a previous run to be repeated, and prepare `workflow_dispatch` with a guard for `development`.
- **Outcome:** Chosen.
- **Reasons:** A development push can run the tests without an image build or a change to `master`. Re-running a completed run provides an immediate manual option, and `workflow_dispatch` can provide an independent manual start once the workflow file is also on the default branch.

### 2. Use only `workflow_dispatch` immediately

- **Description:** Make a manually started workflow the only development test trigger.
- **Outcome:** Not used as the sole initial trigger.
- **Reasons:** GitHub requires the workflow file to exist on the default branch before a new `workflow_dispatch` event can run. At the decision time the file was to be added only to `development`.

### 3. Rely on the existing `master` workflow

- **Description:** Continue to use the existing test, image build, and publication workflow.
- **Outcome:** Not selected as the development test workflow.
- **Reasons:** Its configured triggers do not cover pushes to `development`, and it includes image-related steps beyond the requested test-only execution.

## Decision

Provide a separate GitHub Actions workflow that runs the complete Python test suite on pushes to `development`. Use the application's Python 3.14 version and the existing runtime requirements. Include `workflow_dispatch` and guard the test job so it runs only for the `development` ref. Do not build or publish an image in this workflow.

Local execution of all tests, an individual test file, or an individual test remains available. A previous GitHub run can be repeated on its original commit. A new independent manual dispatch requires the workflow file to exist on the repository's default branch.

## Rationale

The selected approach provides immediate automated feedback on `development` and keeps the test job separate from image publication. The existing run can be repeated without modifying `master`; preparing manual dispatch supports a later independent start once GitHub's default-branch requirement is met.

## Consequences

- Each push to `development` runs the complete tests without an image build or publication.
- Re-running an existing run checks the same commit, not automatically a newer branch head.
- Manual dispatch is configured but cannot start a new run while the workflow file is absent from the default branch.
- This decision does not establish a general branch, review, merge, or release policy. Implementation progress and subsequent changes are tracked in the related issue.

## Relationship to previous decisions

No earlier decision record is superseded. The tests in [issue #25](https://github.com/saschatrebbin/simple-servicetag-generator/issues/25) were the immediate motivation; see also [the APP_DEBUG decision](0001-parse-app-debug-as-boolean.md).

## Additional references

- [Testing workflow](../workflows.md#running-tests)
- [GitHub: manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [GitHub: re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
