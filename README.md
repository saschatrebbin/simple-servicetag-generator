# simple-servicetag-generator

A small web service for generating identifiers and passwords, originally also used for naming XCOM 2 campaigns.

## V2 identifier

`GET /v2/identifier` and `GET /api/v2/identifier` generate a human-readable identifier and an abbreviation from the same randomly selected words and digits. Without a format suffix, the response is plain text. Add `.text`, `.json`, `.html`, `.csv`, or `.xml` to the path to select a format.

Example:

```text
GET /api/v2/identifier?words=5&numbers=3&prefix=CASE-
CASE-Delta-Sierra-India-Delta-Zulu-253 (CASE-DSIDZ-253)
```

| Query parameter | Default | Accepted values | Meaning |
| --- | --- | --- | --- |
| `words` | `5` | `1`–`20` | Number of words drawn independently with replacement from the shared word list. |
| `numbers` | `3` | `0`–`20` | Number of digits; leading zeroes are preserved. Zero omits the number and its separator. |
| `count` | `1` | `1`–`1000` | Number of identifier pairs. |
| `separator` | `-` | One character from Python's `string.punctuation` | Separates the long-form words and number, and the short-form letters and number. URL-encode special characters as needed. |
| `prefix` | empty | At most 64 characters, without control characters | Added verbatim to both forms; include any desired delimiter in the prefix. |

JSON always returns an `identifiers` array, including for a single result, with `long` and `short` fields and the requested parameters as metadata. CSV contains `long` and `short` columns. Text contains one `long (short)` pair per line. HTML provides copy buttons for both forms. XML contains a list of identifier elements.

The service is a generator, not a registry. For a single request, short forms are checked for duplicates and regenerated within a bounded number of attempts. Identifiers are **not guaranteed to be unique across requests or installations**. The caller or receiving system is responsible for checking and enforcing any required uniqueness. Fixed prefixes do not add randomness. An impossible number of distinct results returns HTTP 400. Exhausting the retry budget returns HTTP 503; reduce `count` or increase `words` or `numbers`. Invalid parameters and unsupported formats return HTTP 400.

The shared word list now includes `golf`; consequently, it can also occur in existing endpoints. The identifier is not intended to be a secret or an authorization mechanism.

## Tests and container

Run `python -m unittest discover -s tests -v` with the application's dependencies installed (`pip install -r app/requirements.txt`). The publishing workflow runs these tests with Python 3.9 before building and pushing an image. The Dockerfile copies only the application and its runtime requirements; tests and test output are also excluded from the Docker build context.

Further documentation of the existing endpoints and project architecture is tracked separately in [#1](https://github.com/saschatrebbin/simple-servicetag-generator/issues/1) and [#3](https://github.com/saschatrebbin/simple-servicetag-generator/issues/3).
