import datetime
import math
import time
import random
import string
import secrets
import os
import json
import csv
import html
import io
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import bottle
from bottle import route, run, request, response, HTTPError

secure_random = random.SystemRandom()
start_time = time.time()
request_count = 0

prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
upper_limit = 999
padding = 3

@route('/health')
def health_check():
    global request_count

    uptime = time.time() - start_time
    
    response.content_type = 'application/json'
    return json.dumps({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'uptime_seconds': round(uptime, 2),
        'requests_processed': request_count
    })

# Middleware zum Zählen der Anfragen
@bottle.hook('after_request')
def count_request():
    global request_count
    request_count += 1

# v1 routes
@route('/v1/servicetag')
@route('/v1/new')
def generate_servicetag():
    basic_id_parts = []
    basic_id_parts.append(secrets.choice(prefixlist_international))
    basic_id_parts.append("-")
    basic_id_parts.append(str(secrets.randbelow(1000)).zfill(3))
    basic_id = "".join(basic_id_parts)
    return "{0}".format(basic_id)

@route('/v1/simplepassword')
@route('/v1/simple-password')
def generate_simple_password():
    basic_id_parts = []
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(str(secrets.randbelow(1000)).zfill(3))
    basic_id = "".join(basic_id_parts)
    return "{0}".format(basic_id)

@route('/v1/longpassword')
@route('/v1/long-password')
def generate_long_password():
    basic_id_parts = []
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(secrets.choice(prefixlist_international).capitalize())
    basic_id_parts.append("-")
    basic_id_parts.append(str(secrets.randbelow(1000)).zfill(3))
    basic_id = "".join(basic_id_parts)
    return "{0}".format(basic_id)

@route('/v1/short-token')
def generate_short_token():
    return "{0}".format("#" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9)))

# v2 routes
def _generate_word_parts(word_count, number_count):
    """Choose the words and number block once for all representations."""
    words = [secrets.choice(prefixlist_international).capitalize()
             for _ in range(word_count)]
    number = (str(secrets.randbelow(10 ** number_count)).zfill(number_count)
              if number_count > 0 else None)
    return words, number


def generate_password(word_count=2, number_count=3, separator="-"):
    """Generate a password with the specified parameters."""
    words, number = _generate_word_parts(word_count, number_count)
    return separator.join(words + ([number] if number is not None else []))

def format_response(password, format_type):
    """Format the password according to the requested format"""
    if format_type == 'json':
        response.content_type = 'application/json'
        return json.dumps({'password': password})

    elif format_type == 'xml':
        response.content_type = 'application/xml'
        root = Element('response')
        password_elem = SubElement(root, 'password')
        password_elem.text = password
        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        return xml_str

    elif format_type == 'csv':
        response.content_type = 'text/csv'
        return f"password\n{password}"

    elif format_type == 'html':
        response.content_type = 'text/html'
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Generated Password</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
        .password {{ font-size: 24px; padding: 20px; background-color: #f5f5f5; display: inline-block; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Generated Password</h1>
    <div class="password">{password}</div>
</body>
</html>"""

    else:  # Default to plain text
        response.content_type = 'text/plain'
        return password

@route('/v2/password')
@route('/v2/password.<format_type>')
def v2_password(format_type='text'):
    """Generate a password with customizable parameters"""
    # Get query parameters with defaults
    word_count = int(request.query.get('words', 2))
    number_count = int(request.query.get('numbers', 3))
    separator = request.query.get('separator', '-')

    # Validate parameters
    if word_count < 1:
        return HTTPError(400, "Word count must be at least 1")

    if number_count < 0:
        return HTTPError(400, "Number count must be non-negative")

    if len(separator) != 1 or not all(c in string.punctuation for c in separator):
        return HTTPError(400, "Separator must be a single punctuation character")

    # Generate password
    password = generate_password(word_count, number_count, separator)

    # Format response according to requested format
    return format_response(password, format_type)

@route('/api/v2/password')
@route('/api/v2/password.<format_type>')
def api_v2_password(format_type='text'):
    """Alternative route with /api prefix"""
    return v2_password(format_type)


# ---------------------------------------------------------------------------
# Identifier: one set of random components, two related representations.
# ---------------------------------------------------------------------------

def _identifier_generate_one(word_count, number_count, separator, prefix):
    words, number = _generate_word_parts(word_count, number_count)
    long_parts = words + ([number] if number is not None else [])
    short_parts = ["".join(word[0].upper() for word in words)]
    if number is not None:
        short_parts.append(number)
    return {
        "long": prefix + separator.join(long_parts),
        "short": prefix + separator.join(short_parts),
    }


class IdentifierGenerationExhausted(Exception):
    """The bounded random retry budget was exhausted."""


def _identifier_generate_unique(count, words, numbers, separator, prefix):
    # Distinct initials determine the short form, even if the word list changes.
    pool_size = len({word[0].upper() for word in prefixlist_international}) ** words * 10 ** numbers
    if count > pool_size:
        raise ValueError("'count' exceeds the number of possible short identifiers.")
    identifiers, seen = [], set()
    # Limit work even when the requested count nearly exhausts the available pool.
    for _ in range(max(1000, count * 100)):
        item = _identifier_generate_one(words, numbers, separator, prefix)
        if item["short"] not in seen:
            identifiers.append(item)
            seen.add(item["short"])
            if len(identifiers) == count:
                return identifiers
    raise IdentifierGenerationExhausted("Unable to generate enough distinct short identifiers; reduce count or increase words or numbers.")


def _identifier_format_response(identifiers, meta, format_type):
    if format_type == 'json':
        response.content_type = 'application/json'
        return json.dumps(dict(identifiers=identifiers, **meta))
    if format_type == 'xml':
        response.content_type = 'application/xml'
        root = Element('response')
        SubElement(root, 'count').text = str(len(identifiers))
        entries = SubElement(root, 'identifiers')
        for item in identifiers:
            entry = SubElement(entries, 'identifier')
            SubElement(entry, 'long').text = item['long']
            SubElement(entry, 'short').text = item['short']
        return minidom.parseString(tostring(root)).toprettyxml(indent='  ')
    if format_type == 'csv':
        response.content_type = 'text/csv; charset=utf-8'
        output = io.StringIO(newline='')
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['long', 'short'])
        for item in identifiers:
            writer.writerow([item['long'], item['short']])
        return output.getvalue()
    if format_type == 'html':
        response.content_type = 'text/html; charset=utf-8'
        rows = []
        for i, item in enumerate(identifiers):
            long_value, short_value = html.escape(item['long']), html.escape(item['short'])
            rows.append(f'<li><span id="long-{i}">{long_value}</span> '
                        f'(<span id="short-{i}">{short_value}</span>) '
                        f'<button type="button" onclick="copyValue({i}, \'long\')">Langform kopieren</button> '
                        f'<button type="button" onclick="copyValue({i}, \'short\')">Kurzform kopieren</button> '
                        f'<button type="button" onclick="copyValue({i}, \'both\')">Beide kopieren</button></li>')
        return """<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><title>Identifier</title>
<style>body { font-family: Arial, sans-serif; margin: 3em auto; max-width: 70em; padding: 0 1em; }
li { padding: .7em 0; } button { margin: .2em; cursor: pointer; } span { font-family: monospace; }</style>
</head><body><h1>Identifier</h1><ul>""" + ''.join(rows) + """</ul>
<button type="button" onclick="copyAll()">Alle kopieren</button>
<script>
function value(i, part) { return document.getElementById(part + '-' + i).textContent; }
function copyValue(i, part) {
  const text = part === 'both' ? value(i, 'long') + ' (' + value(i, 'short') + ')' : value(i, part);
  navigator.clipboard.writeText(text);
}
function copyAll() {
  const items = document.querySelectorAll('li');
  navigator.clipboard.writeText(Array.from(items, (_, i) => value(i, 'long') + ' (' + value(i, 'short') + ')').join('\\n'));
}
</script></body></html>"""
    response.content_type = 'text/plain; charset=utf-8'
    return ''.join(item['long'] + ' (' + item['short'] + ')\n' for item in identifiers)


@route('/v2/identifier')
@route('/v2/identifier.<format_type>')
@route('/api/v2/identifier')
@route('/api/v2/identifier.<format_type>')
def v2_identifier(format_type='text'):
    if format_type not in ('text', 'json', 'html', 'csv', 'xml'):
        return HTTPError(400, "Unsupported format; use text, json, html, csv or xml.")
    try:
        words = int(request.query.get('words', 5))
        numbers = int(request.query.get('numbers', 3))
        count = int(request.query.get('count', 1))
    except (ValueError, TypeError):
        return HTTPError(400, "'words', 'numbers' and 'count' must be integers.")
    if not 1 <= words <= 20 or not 0 <= numbers <= 20 or not 1 <= count <= 1000:
        return HTTPError(400, "'words' must be 1-20, 'numbers' 0-20 and 'count' 1-1000.")
    separator = request.query.get('separator', '-')
    if len(separator) != 1 or separator not in string.punctuation:
        return HTTPError(400, "'separator' must be a single punctuation character.")
    prefix = request.query.get('prefix', '')
    # Control characters would make line-oriented text and XML ambiguous or invalid.
    if len(prefix) > 64 or any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in prefix):
        return HTTPError(400, "'prefix' must be at most 64 characters without control characters.")
    try:
        identifiers = _identifier_generate_unique(count, words, numbers, separator, prefix)
    except ValueError as exc:
        return HTTPError(400, str(exc))
    except IdentifierGenerationExhausted as exc:
        return HTTPError(503, str(exc))
    meta = dict(count=count, words=words, numbers=numbers, separator=separator, prefix=prefix)
    return _identifier_format_response(identifiers, meta, format_type)


# ---------------------------------------------------------------------------
# Nano ID  –  Hilfsfunktionen
# ---------------------------------------------------------------------------

_NANOID_DIGITS  = "0123456789"
_NANOID_LOWER   = "abcdefghijklmnopqrstuvwxyz"
_NANOID_UPPER   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_NANOID_SPECIAL = "-_"

def _nanoid_bool_param(name, default):
    """Liest einen Query-Parameter als Boolean (true/false/1/0)."""
    val = request.query.get(name, "").strip().lower()
    if val in ("true",  "1", "yes"): return True
    if val in ("false", "0", "no"):  return False
    return default

def _nanoid_build_alphabet(digits, lower, upper, special):
    """Setzt das Alphabet aus den gewählten Gruppen zusammen."""
    parts = []
    if digits:  parts.append(_NANOID_DIGITS)
    if lower:   parts.append(_NANOID_LOWER)
    if upper:   parts.append(_NANOID_UPPER)
    if special: parts.append(_NANOID_SPECIAL)
    return "".join(parts)

def _nanoid_generate_one(size, alphabet):
    """
    Erzeugt eine einzelne Nano-ID.
    Bias-freie Zeichenauswahl mit kryptografisch sicherem Zufallsgenerator.
    """
    alphabet_len = len(alphabet)
    mask = (1 << (alphabet_len - 1).bit_length()) - 1
    step = max(1, math.ceil(1.6 * mask * size / alphabet_len))
    result = []
    while len(result) < size:
        pool = secrets.token_bytes(step)
        for byte in pool:
            idx = byte & mask
            if idx < alphabet_len:
                result.append(alphabet[idx])
                if len(result) == size:
                    break
    return "".join(result)

def _nanoid_generate_unique(count, size, alphabet, prefix, suffix):
    """Erzeugt `count` garantiert eindeutige IDs; Duplikate werden nachgeneriert."""
    seen = set()
    ids  = []
    while len(ids) < count:
        raw = _nanoid_generate_one(size, alphabet)
        if raw not in seen:
            seen.add(raw)
            ids.append(f"{prefix}{raw}{suffix}")
    return ids

def _nanoid_collision_probability(count, alphabet_size, id_length):
    """
    Wahrscheinlichkeit mindestens einer Kollision (Birthday-Problem-Näherung).
    Rückgabe als Prozentwert (float).
    """
    pool_size = alphabet_size ** id_length
    if pool_size == 0:
        return 100.0
    exponent = -(count * (count - 1)) / (2 * pool_size)
    return (1.0 - math.exp(exponent)) * 100.0

def _nanoid_format_response(ids, col_prob_pct, meta, format_type):
    """
    Gibt die ID-Liste im gewünschten Format zurück.
    meta = dict mit length, count, alphabet_size für XML/CSV/HTML.
    """
    count        = len(ids)
    col_str      = f"{col_prob_pct:.6f}%"
    single       = ids[0] if count == 1 else None

    if format_type == 'json':
        response.content_type = 'application/json'
        return json.dumps({
            "ids":                   ids,
            "count":                 count,
            "length":                meta["length"],
            "alphabet_size":         meta["alphabet_size"],
            "collision_probability": col_str,
        })

    elif format_type == 'xml':
        response.content_type = 'application/xml'
        root = Element('response')
        SubElement(root, 'count').text             = str(count)
        SubElement(root, 'length').text            = str(meta["length"])
        SubElement(root, 'alphabet_size').text     = str(meta["alphabet_size"])
        SubElement(root, 'collision_probability').text = col_str
        ids_elem = SubElement(root, 'ids')
        for id_val in ids:
            SubElement(ids_elem, 'id').text = id_val
        return minidom.parseString(tostring(root)).toprettyxml(indent="  ")

    elif format_type == 'csv':
        response.content_type = 'text/csv'
        lines = ["id"]
        lines.extend(ids)
        # Metadaten als Kommentarzeilen am Ende
        lines.append(f"# collision_probability: {col_str}")
        return "\n".join(lines) + "\n"

    elif format_type == 'html':
        response.content_type = 'text/html'
        if count == 1:
            ids_html = f'<div class="id-value" id="id-0">{ids[0]}</div>'
        else:
            items = "".join(
                f'<li><span class="id-value" id="id-{i}">{v}</span>'
                f'<button class="copy-btn" onclick="copyOne({i})">Kopieren</button></li>'
                for i, v in enumerate(ids)
            )
            ids_html = f'<ul class="id-list">{items}</ul>'

        copy_all_btn = (
            '<button class="copy-btn copy-all" onclick="copyAll()">Alle kopieren</button>'
            if count > 1 else
            '<button class="copy-btn" onclick="copyOne(0)">Kopieren</button>'
        )

        return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Nano IDs</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; color: #333; }}
        h1   {{ margin-bottom: 0.25em; }}
        .meta {{ font-size: 0.85em; color: #888; margin-bottom: 1.5em; }}
        .id-value {{ font-family: monospace; font-size: 1.2em; }}
        .id-list {{ list-style: none; padding: 0; display: inline-block; text-align: left; }}
        .id-list li {{ display: flex; align-items: center; gap: 0.75em;
                       padding: 0.4em 0.6em; border-bottom: 1px solid #eee; }}
        .id-list li:last-child {{ border-bottom: none; }}
        .copy-btn {{ cursor: pointer; padding: 0.25em 0.75em; font-size: 0.8em;
                     border: 1px solid #aaa; border-radius: 4px; background: #f5f5f5; }}
        .copy-btn:hover {{ background: #e0e0e0; }}
        .copy-all {{ font-size: 1em; margin-top: 1.2em; padding: 0.4em 1.2em; }}
        .single-box {{ font-size: 1.5em; padding: 20px 32px; background: #f5f5f5;
                       display: inline-block; border-radius: 6px; margin-bottom: 1em; }}
    </style>
</head>
<body>
    <h1>Nano IDs</h1>
    <p class="meta">
        {count} ID{'s' if count > 1 else ''} &nbsp;|&nbsp;
        Länge: {meta['length']} &nbsp;|&nbsp;
        Alphabet: {meta['alphabet_size']} Zeichen &nbsp;|&nbsp;
        Kollisionswahrsch.: {col_str}
    </p>
    {'<div class="single-box">' + ids_html + '</div>' if count == 1 else ids_html}
    {copy_all_btn}
    <script>
        function copyOne(i) {{
            const el = document.getElementById('id-' + i);
            navigator.clipboard.writeText(el.innerText).then(() => {{
                el.style.background = '#d4edda';
                setTimeout(() => el.style.background = '', 1000);
            }});
        }}
        function copyAll() {{
            const els = document.querySelectorAll('.id-value');
            const text = Array.from(els).map(e => e.innerText).join('\\n');
            navigator.clipboard.writeText(text);
        }}
    </script>
</body>
</html>"""

    else:  # plain text
        response.content_type = 'text/plain; charset=utf-8'
        comment = f"# collision_probability: {col_str} (count={count}, alphabet={meta['alphabet_size']}, length={meta['length']})\n"
        return comment + "\n".join(ids) + "\n"


# ---------------------------------------------------------------------------
# Nano ID  –  Route
#
# Query-Parameter:
#   length   – Länge der ID (ohne Präfix/Suffix), Default 21, min 1
#   count    – Anzahl der IDs, Default 1, max 1000
#   digits   – Ziffern 0-9 einschließen          (Default: true)
#   lower    – Kleinbuchstaben a-z               (Default: true)
#   upper    – Großbuchstaben A-Z                (Default: true)
#   special  – Sonderzeichen - _                 (Default: false)
#   prefix   – Präfix für jede ID                (Default: "")
#   suffix   – Suffix für jede ID                (Default: "")
#
# Beispiele:
#   /api/v2/nanoid?length=12&upper=true&lower=false&count=50
#   /api/v2/nanoid.json?length=8&prefix=DOC-&count=10
#   /api/v2/nanoid.html?length=10&upper=true&lower=false&count=5
# ---------------------------------------------------------------------------

@route('/api/v2/nanoid')
@route('/api/v2/nanoid.<format_type>')
def api_v2_nanoid(format_type='text'):
    """Nano-ID-Generator mit konfigurierbarem Alphabet, Länge und Menge."""

    # --- Parameter einlesen & validieren ---
    try:
        length = int(request.query.get('length', 21))
        count  = int(request.query.get('count',   1))
    except ValueError:
        return HTTPError(400, "Parameter 'length' und 'count' müssen ganzzahlig sein.")

    if length < 1:
        return HTTPError(400, "'length' muss mindestens 1 sein.")

    if count < 1 or count > 1000:
        return HTTPError(400, "'count' muss zwischen 1 und 1000 liegen.")

    digits  = _nanoid_bool_param('digits',  default=True)
    lower   = _nanoid_bool_param('lower',   default=True)
    upper   = _nanoid_bool_param('upper',   default=True)
    special = _nanoid_bool_param('special', default=False)

    prefix = request.query.get('prefix', '')
    suffix = request.query.get('suffix', '')

    alphabet = _nanoid_build_alphabet(digits, lower, upper, special)
    if not alphabet:
        return HTTPError(400, "Mindestens eine Alphabet-Gruppe muss aktiviert sein.")

    # --- IDs generieren ---
    ids = _nanoid_generate_unique(count, length, alphabet, prefix, suffix)

    # --- Kollisionswahrscheinlichkeit ---
    col_prob_pct = _nanoid_collision_probability(count, len(alphabet), length)

    meta = {
        "length":        length,
        "alphabet_size": len(alphabet),
    }

    return _nanoid_format_response(ids, col_prob_pct, meta, format_type)


if __name__ == '__main__':
    run(host=os.getenv('APP_IP', '0.0.0.0'), port=os.getenv('APP_PORT', '3000'), debug=os.getenv('APP_DEBUG', 'false'))
