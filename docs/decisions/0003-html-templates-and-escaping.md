# Render HTML responses with Bottle templates

- **Status:** Valid
- **Status date:** 2026-11-28
- **Decision date:** 2026-11-28
- **Decided by:** Sascha Trebbin (maintainer)
- **Related issue:** [#19 — Reflected XSS in the Nano ID HTML output](https://github.com/saschatrebbin/simple-servicetag-generator/issues/19)

## Context and question

The Nano ID HTML response inserted a caller-controlled prefix and suffix into HTML without escaping. The password HTML response could also insert a separator that affects markup. The Identifier response already escaped values, but all three pages were assembled inside Python code. The service needs safe HTML text output and a clearer, consistent separation between presentation and Python logic.

## Options considered

### Escape values in Python and keep HTML in the handlers

- **Description:** Apply explicit HTML escaping in the existing response-building code, following the Identifier's established approach.
- **Outcome:** Not chosen.
- **Reasons:** It can protect the current HTML text values, but leaves presentation and Python logic interwoven and the separate HTML pages harder to standardize.

### Use Bottle SimpleTemplate files

- **Description:** Move the V2 HTML pages to individual Bottle templates with shared page and clipboard components, using the normal escaped template output for dynamic values.
- **Outcome:** Chosen.
- **Reasons:** It addresses the HTML text escaping requirement and separates and standardizes the presentation using the existing Bottle dependency.

## Decision

Keep V2 HTML templates under `app/templates/`, with individual Nano ID, Identifier, and password pages and shared components. Resolve their lookup path relative to the application module and include the templates in the container image. Apply this approach to future HTML pages.

Pass dynamic values as data and use normal escaped template expressions for HTML text. Do not use unescaped template expressions. Do not insert user-controlled values into template source, inline JavaScript, or event handlers; a new context requires the appropriate context-specific encoding. This protects the HTML output independently of future input validation. Other response formats keep their own existing formatting.

Use a shared clipboard component that reads text with `textContent` to preserve normal spaces. Test HTML output and the clipboard component locally and in the test workflow; the clipboard tests use Node.js with a simulated DOM and clipboard. Verify template packaging separately when the container image is built.

## Rationale

The selected solution protects dynamic HTML text while making presentation easier to find and maintain. Bottle is already a dependency, and a shared component avoids separately maintaining the same clipboard logic on each page.

## Consequences

- Templates become runtime files and must be shipped alongside the application.
- HTML special characters are displayed as data and copied without HTML entity encoding; ordinary leading, trailing, and repeated spaces are preserved.
- Node.js is needed to run the complete test suite, but not to run the service.
- Simulated DOM and clipboard tests do not replace full browser or container tests.
- Input validation, common parameter conventions, the Nano ID CSV issue, and a possible diagnostic endpoint remain separate topics.

## Relationship to previous decisions

No earlier decision record is superseded. The [development test workflow](0002-development-test-workflow.md) continues to run the full suite without building an image; the suite now also invokes Node.js clipboard tests.

## Additional references

- [Architecture overview and HTML safety](../architecture.md#2-runtime-structure)
- [Running tests](../workflows.md#running-tests)
- [Parameter conventions](https://github.com/saschatrebbin/simple-servicetag-generator/issues/30), [input validation](https://github.com/saschatrebbin/simple-servicetag-generator/issues/31), [Nano ID CSV](https://github.com/saschatrebbin/simple-servicetag-generator/issues/32), [diagnostic endpoint](https://github.com/saschatrebbin/simple-servicetag-generator/issues/33)
