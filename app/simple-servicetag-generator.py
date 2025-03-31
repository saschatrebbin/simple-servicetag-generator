import datetime
import time
import random
import string
import secrets
import os
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import bottle
from bottle import route, run, request, response, HTTPError

secure_random = random.SystemRandom()
start_time = time.time()
request_count = 0

prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
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
def generate_password(word_count=2, number_count=3, separator="-"):
    """Generate a password with the specified parameters"""
    parts = []

    # Add words
    for _ in range(word_count):
        parts.append(secrets.choice(prefixlist_international).capitalize())

    # Add numbers
    if number_count > 0:
        parts.append(str(secrets.randbelow(10**number_count)).zfill(number_count))

    # Join with separator
    return separator.join(parts)

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

run(host=os.getenv('APP_IP', '0.0.0.0'), port=os.getenv('APP_PORT', '3000'), debug=os.getenv('APP_DEBUG', 'false'))
