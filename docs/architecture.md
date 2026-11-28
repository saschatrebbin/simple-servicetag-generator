# Architecture overview

This document describes the current implementation of the service and its supporting repository configuration. Update it when those change.

## 1. Purpose and system context

The service provides HTTP endpoints that generate identifiers, tokens, and word-based passwords or passphrases. It is intended primarily for the maintainer's own use. See the [project scope](scope.md) for its purpose and boundaries.

Clients can include a browser, script, or another application. A reverse proxy can be used by a deployment, for example to terminate HTTPS or apply access controls; it is external to this repository. Direct HTTP access to the Bottle service is also possible, depending on the deployment.

```mermaid
flowchart TD
    Client["API client"]
    Proxy["Optional reverse proxy"]
    Service["Python and Bottle service"]
    Random["Operating system randomness"]
    Client -->|"Direct HTTP"| Service
    Client -->|"HTTP or HTTPS"| Proxy
    Proxy -->|"HTTP"| Service
    Service -->|"Python secrets"| Random
```

## 2. Runtime structure

The application is implemented in a single Python source file, `app/simple-servicetag-generator.py`. Bottle supplies the HTTP routing and request/response objects. The diagram groups functions by responsibility; the boxes are not separate deployed services or Python modules.

```mermaid
flowchart TD
    Router["Bottle routing"]
    Router --> Health["Health endpoint"]
    Router --> V1["V1 generators"]
    Router --> V2["V2 generators"]
    Health --> Runtime["Process runtime state"]
    V1 --> Secrets["Python secrets"]
    V1 --> Words["Shared word list"]
    V2 --> WordBased["Password and identifier"]
    V2 --> Nano["Nano ID"]
    V2 --> Formats["Formatters per endpoint"]
    Formats --> Templates["Bottle HTML templates"]
    WordBased --> Common["Word and digit generation"]
    Common --> Words
    Common --> Secrets
    Nano --> Secrets
```

- **Routing and validation:** Bottle selects a registered route. Each handler reads and validates its own parameters; validation behaviour is currently not identical across all V2 handlers.
- **Generation:** V1 routes generate service tags, word-based passwords, or short tokens. V2 password and identifier generation share the helper that selects words and digits. Nano ID has its own alphabet and character-generation helpers. Random selection uses Python's `secrets` module and the operating system's randomness source.
- **Formatting:** V1 handlers return simple text values. Each V2 generator has its own response-formatting function supporting some of text, JSON, XML, CSV, and HTML. These are separate implementations, not one common formatting module, and supported formats differ by endpoint.
- **HTML:** V2 HTML responses use Bottle SimpleTemplate files in `app/templates/`. The handlers pass values to endpoint-specific templates, which include shared page and clipboard components. Templates are looked up relative to the application module rather than the working directory. The Dockerfile copies them into `/code/templates/`. They are supporting presentations of API results, not a separately deployed frontend application.
- **Safe HTML values:** Template files and the shared JavaScript are trusted application code. Dynamic result values are passed as data and rendered in HTML text with SimpleTemplate's normal `{{...}}` escaping; do not disable escaping with `{{!...}}`. For any new output context, apply encoding appropriate to that context instead of inserting data into template source, inline JavaScript, or event handlers. The clipboard reads the displayed values via `textContent`, retaining ordinary leading, trailing, and repeated spaces. This output protection is independent of input validation and does not apply HTML escaping to the other response formats. See the [HTML template decision](decisions/0003-html-templates-and-escaping.md).
- **Health:** `/health` returns JSON containing a health status, timestamp, uptime, and a request count.

## 3. API groups and request handling

| Route group | Responsibility |
|---|---|
| `/health` | Health information and process-local counters. |
| `/v1/...` | Existing service tag, word-based password, and short-token generators, including existing aliases. |
| `/v2/password` and `/api/v2/password` | Configurable word-based password generation. |
| `/v2/identifier` and `/api/v2/identifier` | Long and short identifier forms derived from the same random parts. |
| `/api/v2/nanoid` | Configurable Nano ID generation. |

A typical generator request is routed to a handler, which reads its parameters, generates the requested value or values, and formats an HTTP response. The precise validation, output fields, suffix handling, and error behaviour depend on the handler.

## 4. State and storage

The application currently has **no implemented database, persistent result store, or registry of generated IDs**. It does not save generated values for later requests. This statement concerns the application code; browser caches, deployment logs, reverse proxies, and downstream systems may have their own storage behaviour.

There is nevertheless temporary in-memory state:

- `start_time` and `request_count` are held in process memory and used by `/health`; a Bottle `after_request` hook increments the request counter.
- The V2 Identifier and Nano ID use request-local sets to detect duplicates when producing multiple results in one response.

These values are not shared across separate processes or installations and do not survive a process restart. The request-local duplicate checks do not provide global uniqueness across requests.

## 5. Configuration and deployment

| Variable | Value passed when unset | Purpose |
|---|---|---|
| `APP_IP` | `0.0.0.0` | Bind address passed to Bottle. |
| `APP_PORT` | `3000` | Port passed to Bottle. |
| `APP_DEBUG` | `False` | Parsed as a Boolean and passed to Bottle's debug argument. |

For the regular application start, the variable is case-insensitive and surrounding whitespace is ignored. `true`, `1`, `yes`, and `on` enable debugging; `false`, `0`, `no`, `off`, an empty value, or an unset variable disable it. Other values cause a startup error before the server starts. Debug error responses can expose traceback details when debugging is enabled. The choice and alternatives are recorded in the [APP_DEBUG decision](decisions/0001-parse-app-debug-as-boolean.md).

The checked-in Dockerfile uses `python:3.14-slim`, copies the application, its templates, and `app/requirements.txt` into `/code`, installs the Bottle dependency (`bottle<=0.13`), and runs the Python application. It declares no application data volume. Actual port publishing, reverse proxies, TLS, and any access restrictions are deployment decisions outside the Dockerfile.

The repository also contains a vendored `app/bottle.py` development snapshot. It is not copied into the container image. Local execution can resolve this file differently from the container, and the tests use it as a fallback when no installed Bottle package is found.

### Previous debug behaviour

Before the correction first committed on 2026-11-27, the default string `false` was passed directly to Bottle. Because it is non-empty, it enabled debug mode; setting `APP_DEBUG=false` had the same effect and HTTP errors could expose traceback details. See [issue #25](https://github.com/saschatrebbin/simple-servicetag-generator/issues/25) for the problem and its resolution.

### Previous HTML rendering

Before the change for [issue #19](https://github.com/saschatrebbin/simple-servicetag-generator/issues/19) in November 2026, the handlers built HTML directly in Python strings. The Identifier formatter escaped its values, while the Nano ID and password formatters inserted generated values without HTML escaping. The change moves presentation into templates and consistently escapes dynamic HTML text.

## 6. Security and operational context

The application code does not implement its own authentication, authorization, or rate limiting. A deployment may provide additional protections externally; the repository alone does not establish whether they are present. The standalone Bottle server serves HTTP, while TLS can be supplied by an external component.

Generator randomness, entropy, collision limits, and suitable-use considerations are described in [Cryptographic foundations and limitations](cryptography.md).

## 7. Tests, build, and publication

The GitHub Actions build-and-publish workflow runs for pull requests targeting `master` and pushes to `master`. Its test job installs the runtime dependency and runs the test suite under Python 3.14 and Node.js 24. A following job builds a local image and smoke-tests `/health`, V2 Identifier JSON, and the three V2 HTML pages. Only a successful push to `master` proceeds to the separate build-and-publish job for GitHub Container Registry.

```mermaid
flowchart TD
    Pull["Pull request to master"] --> Tests["Run Python unit tests"]
    Push["Push to master"] --> Tests
    Tests --> Check["Build and smoke-test image"]
    Check --> Event{"Push to master?"}
    Event -->|"Yes"| Publish["Build and publish to GHCR"]
    Event -->|"No"| Done["Checks complete"]
```

The publish job performs its own image build after the smoke-test job. The Python tests cover the V2 Identifier, password regressions, HTML escaping and `APP_DEBUG` startup and HTTP error handling. The same test command invokes Node.js tests for the shared clipboard script with a simulated DOM and clipboard. These are not full browser tests.

A separate test-only workflow runs the full suite under Python 3.14 and Node.js 24 when `development` is pushed or the workflow is manually dispatched for that branch. It neither builds nor publishes an image. See [running tests](workflows.md#running-tests) and the [development test decision](decisions/0002-development-test-workflow.md).

## 8. Related documents

- [Project scope](scope.md)
- [Cryptographic foundations and limitations](cryptography.md)
- [Decision workflow](workflows.md)
- [README](../README.md)



