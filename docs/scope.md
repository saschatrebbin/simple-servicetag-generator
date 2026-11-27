# Project scope

## Purpose and audience

This is a personal service developed primarily by the maintainer for the maintainer's own use. Requirements from other users may be considered, but they are secondary to that purpose.

The service offers an HTTP API that generates values such as identifiers, tokens, passphrases, and passwords. Examples illustrate possible uses; they do not restrict the service to a fixed list of applications.

One original example was naming XCOM campaigns. The same general approach can be useful for campaigns in other games or for other objects that need a distinguishable label.

## Identifiers and tokens

A central goal is to generate identifiers whose random parts do not depend on an object's content or on attributes that may later change. This avoids embedding a meaning in an identifier that may become misleading or difficult to remove when the object changes. Users can still choose an explicit prefix or other configured additions when appropriate for their own use.

The service does not provide a persistent registry or guarantee global uniqueness across requests or installations. A consuming system is responsible for checking or enforcing uniqueness where its use requires it.

## Passwords and passphrases

Generating word-based passwords and passphrases is in scope. One example is a readable initial password for an internally operated service, where its suitability has been assessed against that environment's threat model.

The service is not intended to replace a dedicated password generator or password manager. Short configurations may have small search spaces. Longer configurations, such as ten words and three digits, may be assessed for a particular use, but do not come with a general safety guarantee. The generator code and word list are public; a security assessment should not rely on an attacker being unable to discover the generation method.

## API output and interfaces

The API is the main interface. Text and structured formats, suffixes, and HTML output support access to the API and use of its results. Supported formats and suffixes currently vary between endpoints; examples of a format do not imply that every endpoint implements it.

HTML pages should support existing API functionality, for example by presenting a generated result or making it easier to copy. An independent interactive application belongs in a separate web app that may use this API. For example, a page that accepts a word and spells out each letter using an alphabet would be a separate application feature, not merely a presentation of a generated result.

Additional word and spelling alphabets are within the intended project scope. Inclusion in the intended scope does not mean that a particular alphabet is currently implemented.

## Security, uniqueness, and responsibility

The API generates values; it does not guarantee that a particular value is sufficiently secure for every purpose, that transport is secure in every deployment, or that a value is used or stored safely afterward. Nor does it ensure global uniqueness. These boundaries do not remove the need to implement the service carefully or to address known weaknesses.

Operators and users must assess their own threat model and decide:

- Whether and how the service should be reachable.
- Which generator and parameters are suitable for a particular purpose.
- How generated values are transmitted, stored, and protected.
- How required uniqueness is checked or enforced by consuming systems.

See [Cryptographic foundations and limitations](cryptography.md) for the implemented randomness, result spaces, and collision examples. The [architecture overview](architecture.md) describes the current implementation. Important decisions are documented through the [decision workflow](workflows.md). The [README](../README.md) is the repository entry point.
