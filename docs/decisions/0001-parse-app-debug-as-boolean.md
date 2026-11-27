# Parse APP_DEBUG as a boolean at startup

- **Status:** Valid
- **Status date:** 2026-11-27
- **Decision date:** 2026-11-27
- **Decided by:** Sascha Trebbin (maintainer)
- **Related issue:** [#25 — APP_DEBUG=false enables Bottle debug mode](https://github.com/saschatrebbin/simple-servicetag-generator/issues/25)

## Context and question

The regular application start passed `APP_DEBUG` directly to Bottle as a string. Its default, `false`, is non-empty and was therefore treated as true, enabling debug output that could expose traceback details in HTTP error responses. The decision concerns how to configure debug mode explicitly while preventing accidental activation.

## Options considered

The issue compared the following options. The maintainer selected option 2; individual reasons for not selecting each other option were not recorded. The comparisons below are the trade-offs documented in the issue, not attributed explanations for the selection.

### 1. Treat only `true` as enabled

- **Description:** Keep `APP_DEBUG` and compare the normalized value with `true`.
- **Outcome:** Not selected.
- **Reasons and trade-offs:** The approach is small, but the example would not recognize values such as `1` or `yes` and would silently treat an unknown value as disabled.

### 2. Parse an explicit set of values

- **Description:** Keep `APP_DEBUG`, convert recognized values to a Boolean with a dedicated function, and reject unknown values at startup.
- **Outcome:** Chosen.
- **Reasons and trade-offs:** Explicit values and errors make the configuration predictable. It adds a small amount of application code and causes invalid values to prevent startup.

### 3. Use `configparser` for Boolean conversion

- **Description:** Use the standard library's Boolean conversion rather than a dedicated value table.
- **Outcome:** Not selected.
- **Reasons and trade-offs:** It supports common Boolean spellings without another dependency, but a parser instance adds machinery for a single variable.

### 4. Replace the environment variable with a command-line switch

- **Description:** Enable debug mode with an explicit option such as `--debug`.
- **Outcome:** Not selected.
- **Reasons and trade-offs:** The option would make activation explicit, but would change the configuration interface and require start commands to be adapted.

### 5. Disable debug mode for the regular start

- **Description:** Always pass `False` and remove or ignore `APP_DEBUG` for that start path.
- **Outcome:** Not selected.
- **Reasons and trade-offs:** This prevents accidental activation, but also removes the existing way to enable debugging intentionally.

## Decision

Retain `APP_DEBUG` and parse it as a Boolean before passing it to Bottle. Ignore surrounding whitespace and case. Treat `true`, `1`, `yes`, and `on` as true; treat `false`, `0`, `no`, `off`, and an empty value as false. If the variable is not set, use false. Reject any other value with a clear startup error.

## Rationale

The maintainer selected the dedicated parser. The documented comparison identifies explicit accepted values, early error reporting, and retention of the environment variable as properties of that choice. No further personal rationale was recorded with the selection.

## Consequences

- Bottle receives an actual Boolean and debug mode is off by default.
- Existing deployments that relied on any non-empty value enabling debug mode will behave differently. Unrecognized values now prevent startup.
- Deliberately enabling debug mode can expose diagnostic details in error responses.
- The decision's status is independent of deployment progress; implementation and testing are tracked in the related issue.

## Relationship to previous decisions

No earlier decision record is superseded.

## Additional references

- [Options and selection in issue #25](https://github.com/saschatrebbin/simple-servicetag-generator/issues/25#issuecomment-7227450360)
- [Architecture overview](../architecture.md)
