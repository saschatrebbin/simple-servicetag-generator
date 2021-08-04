import random
import secrets

from bottle import route, run

secure_random = random.SystemRandom()

prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
upper_limit = 999
padding = 3

@route('/v1/servicetag')
@route('/v1/new')
def generate():
	basic_id_parts = []
	basic_id_parts.append(secrets.choice(prefixlist_international))
	basic_id_parts.append("-")
	basic_id_parts.append(str(secrets.randbelow(1000)).zfill(3))
	basic_id = "".join(basic_id_parts)
	return "{0}".format(basic_id)

@route('/v1/simplepassword')
@route('/v1/simple-password')
def generate():
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
def generate():
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
def generate():
	return "{0}".format("#" + secrets.token_urlsafe(7))

run(host='0.0.0.0', port=80, debug=True)
