# Workflows

This document describes the project's decision and test-execution workflows. Other recurring workflows can be agreed and documented when needed.

## Decision workflow

### When to make a record

Use a separate decision record for important decisions, particularly those concerning application or repository architecture, the API, or cryptographic processing. These are guidelines rather than automatic rules: the maintainer decides whether a particular subject needs a record.

An editorial correction that leaves the meaning unchanged, or a minor clarification, does not automatically require a new decision. Consider the actual change and its consequences.

### Discuss and decide

1. Discuss the question, context, alternatives, and reasons in an appropriate GitHub issue. An existing relevant issue may be used for its initial discussion.
2. Add progress, clarification, and decisions as new comments. Preserve the original issue text so the discussion remains traceable. This practice applies to all issues.
3. Clearly record the outcome in the issue. A decision may be made before its repository documentation or technical implementation is complete.
4. Create an individual Markdown record using the [decision-record template](templates/decision-record.md). Link the issue and other relevant sources. Once available, the record is the durable reference for the decision, and a comment in the issue should link to it.
5. Track implementation progress separately in the related issue or a linked implementation issue. A `Valid` decision does not imply that the work has already been implemented or specify when it will be implemented.

Record the alternatives actually considered, which were chosen or not chosen, and the reasons at the time. If no other alternatives were considered, say so. Do not invent alternatives, approval, dates, or rationale that cannot be substantiated.

### Location and names

Keep records in [`docs/decisions/`](decisions/) as separate files named with a sequential number and a short descriptive name, for example `0001-descriptive-name.md`. The number represents the order in which records were created; it is not the issue number. The decision date inside the record establishes when the decision was made.

The directory listing is the overview. No separate manually maintained or automatically generated index is required. When the first record is added, the directory placeholder can be removed.

### Record fields and statuses

Each record includes its status and status date, decision date, decision maker, related issue, context and question, alternatives and reasons, decision, rationale, consequences, and relevant references. Where a date or decision maker is not yet known, mark it as pending rather than guessing.

| Status | Meaning |
|---|---|
| `Proposed` | The proposal has not yet been accepted. |
| `Valid` | The decision has been made and currently applies. |
| `Superseded` | A later decision has replaced it. |
| `Revoked` | It no longer applies, without necessarily having an immediate replacement. |
| `Rejected` | The proposal was not accepted. |

The **decision date** records when the decision was made. The **status date** records when the current status took effect or was last changed. Keep the original decision date when the status changes.

### Revisit a completed decision

For a later new or substantively changed decision, use a new issue to capture the discussion and create a new decision record. Link the previous records and their related issues from the new record, explaining what is being replaced or revoked and why.

Keep each earlier record in place as its historical account. If its status changes, update only its status and status date; leave its original content and decision date intact. A review alone does not make the earlier decision obsolete. If only part is replaced, make the scope clear in the new record and choose the earlier record's status to reflect what remains applicable.

The earlier issue remains a completed historical record. An additional comment may link to the new issue and decision; reopening or rewriting the earlier issue is not required. Update other affected current documentation when the new state takes effect, while preserving relevant history in accordance with `AGENTS.md`.

## Running tests

Install the application's runtime dependency from the repository root, then run the full suite:

```bash
python -m pip install -r app/requirements.txt
python -m unittest discover -s tests -v
```

Run one test file or one test case when a narrower check is useful:

```bash
# One test file
python -m unittest discover -s tests -p test_debug.py -v

# One test case
python tests/test_debug.py DebugStartupTests.test_invalid_values_fail_before_server_start -v
```

The [development test workflow](../.github/workflows/test-development.yml) runs the complete suite on Python 3.14 when a commit is pushed to `development`. It does not build or publish a container image.

In GitHub Actions, a completed run can be repeated with **Re-run jobs** or **Re-run all jobs**. A repeated run uses the same commit as the original, not necessarily the latest branch head. GitHub permits re-runs within 30 days of the initial run.

The workflow also defines `workflow_dispatch`, with the test job limited to the `development` ref. GitHub requires the workflow file to exist on the repository's default branch before a new manual run can be started with **Run workflow**. Until then, use a development push or repeat an existing run. See [GitHub's manual-run documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) and the [decision record](decisions/0002-development-test-workflow.md).

