# Cryptographic foundations and limitations

## 1. Purpose and scope

This document explains the randomness sources, result spaces, collision behaviour, and practical limitations of the service's V1 and V2 generators. It describes the current implementation in this repository and should be updated when the implementation changes.

The figures help assess a generator and its parameters for a particular use case. They are not a general guarantee that a generated value is suitable for every security-sensitive purpose.

## 2. Randomness sources

The current generators use Python's `secrets` module:

- `secrets.choice()` selects words or characters.
- `secrets.randbelow()` selects a number within the configured range.
- `secrets.token_bytes()` supplies random bytes for Nano ID character selection.

Python documents `secrets` as using the operating system's secure randomness source: [Python 3.14: secrets](https://docs.python.org/3.14/library/secrets.html). The selection logic is in the [generator source](../app/simple-servicetag-generator.py).

A cryptographically secure randomness source does not make a small result space large. If a configuration can produce only 26,000 different values, there are still only 26,000 possibilities.

## 3. Result space and entropy

The result space is the set of values a given configuration can produce. Under the assumptions of uniform selection and fixed, known parameters, the entropy of one independent draw is:

`entropy in bits = log2(number of possible results)`

The following figures describe the current implementation and default parameters. A fixed, known separator, prefix, suffix, or capitalization does not add random entropy.

| Generator | Default structure | Possible results | Entropy per independent result |
|---|---|---:|---:|
| V1 Servicetag | 1 of 26 words and 3 digits | 26,000 | approx. 14.7 bits |
| V1 Simple Password | 2 of 26 words and 3 digits | 676,000 | approx. 19.4 bits |
| V1 Long Password | 5 of 26 words and 3 digits | 11,881,376,000 | approx. 33.5 bits |
| V1 Short Token | 9 characters from 36 possibilities and a fixed `#` prefix | 101,559,956,668,416 | approx. 46.5 bits |
| V2 Password | 2 of 26 words and 3 digits | 676,000 | approx. 19.4 bits |
| V2 Identifier | 5 of 26 words and 3 digits | 11,881,376,000 | approx. 33.5 bits |
| V2 Nano ID | 21 characters from 62 possibilities | approx. 4.37 × 10^37 | approx. 125.0 bits |

The V2 Identifier's long and short forms are derived from the **same** random words and digits. Their entropy must not be added together. With the current word list, every word has a distinct initial, so the short form currently has the same number of possibilities as the long form. This relationship must be reviewed if the word list changes. See the [generator source](../app/simple-servicetag-generator.py).

### Example: the default word-based password

```text
26 possibilities for the first word
× 26 possibilities for the second word
× 1,000 possibilities for the number block
= 676,000 possible passwords

log2(676,000) ≈ 19.4 bits
```

The length of the written words does not change the fact that each word is selected from a known list of 26 possibilities.

## 4. Effect of parameters

### Word-based generators

With the current 26-word list, the number of possibilities for one independently generated value is:

`number of possible results = 26 ^ word count × 10 ^ digit count`

| Configuration | Possible results | Entropy |
|---|---:|---:|
| 2 words, 3 digits | 676,000 | approx. 19.4 bits |
| 4 words, 3 digits | 456,976,000 | approx. 28.8 bits |
| 5 words, 3 digits | 11,881,376,000 | approx. 33.5 bits |

### Nano ID

The result space depends on the selected alphabet and the generated ID length:

`number of possible results = alphabet size ^ length`

The default alphabet contains 62 characters: digits, lowercase letters, and uppercase letters. The default length is 21 characters. The current implementation derives character indices from random bytes and rejects indices outside the selected alphabet; see the [generator source](../app/simple-servicetag-generator.py).

For comparison, six characters selected from digits alone provide 1,000,000 possible values, or approximately 19.9 bits. The properties of a Nano ID therefore depend on its actual configuration.

## 5. Collisions and uniqueness

A collision occurs when the same value is generated more than once. Distinguish between:

1. Multiple results within a single request.
2. Results generated across separate requests or installations.

The V2 Identifier and Nano ID regenerate duplicates within a multiple-result response. They do not maintain a shared registry across separate requests. A consuming system is responsible for checking or enforcing any required long-term uniqueness.

### Example: 100 independent single-result requests

For a result space of size `N` and `n` independent uniformly selected values, the probability of at least one collision among them is:

`P = 1 - product(1 - k / N), for k = 0 ... n - 1`

The following figures use `n = 100`, fixed default parameters, and 100 separate requests returning one result each:

| Generator | Probability of at least one duplicate among 100 results |
|---|---:|
| V1 Servicetag | approx. 17.36% |
| V1 Simple Password or V2 Password | approx. 0.73% |
| V1 Long Password or V2 Identifier | approx. 0.0000417% |

This is the probability that *any pair* among the 100 results matches. It is not the probability that the next result matches one particular existing value.

### Nano ID collision display

The current Nano ID response calculates a probability using the number requested, alphabet size, and length. For `count=1`, it displays 0%; this does not exclude a collision with a previously generated ID. The calculation concerns the corresponding independent-draw collision model; actual duplicates within one response are regenerated. Rounding and floating-point precision also affect the displayed value.

## 6. Practical interpretation

- A short service tag can be useful as a readable label when duplicate detection or tolerance is available. Its small result space matters for long-term uniqueness.
- The default two-word password has a relatively small search space. Sensitive password use requires an appropriate assessment of the use case and, where suitable, a configuration with more randomness.
- The V2 Identifier is intended for readable long and short identifiers; the README does not describe it as a secret or authorization mechanism.
- The default Nano ID configuration has a large result space, but reducing its length or alphabet changes that assessment.

Generation is only one part of security. The way values are transmitted, stored, exposed, and access-controlled also matters. The guidance here is intentionally brief and does not claim that any particular configuration is universally safe.

## 7. Known limitations

- Nano ID generation can continue indefinitely when the requested number of unique values cannot be produced.
- The Nano ID collision figure describes the model above and is not a guarantee of uniqueness across requests.
- Changes to the word list may change result spaces and the relationship between identifier forms.

See also the [project scope](scope.md), [architecture overview](architecture.md), and [README](../README.md). This description is based on static code inspection and checked examples; it is not a comprehensive security audit.

