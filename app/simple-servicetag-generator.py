import random
from bottle import route, run

secure_random = random.SystemRandom()

prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
upper_limit = 999
padding = 3

@route('/v1/servicetag')
@route('/v1/new')
def hello():
	basic_id_parts = []
	basic_id_parts.append(secure_random.choice(prefixlist_international))
	basic_id_parts.append("-")
	basic_id_parts.append(str(secure_random.randint(-1,upper_limit)).zfill(3))
	basic_id = "".join(basic_id_parts)
	return "{0}".format(basic_id)

@route('/v1/simplepassword')
def hello():
	basic_id_parts = []
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(str(secure_random.randint(-1,upper_limit)).zfill(3))
	basic_id = "".join(basic_id_parts)
	return "{0}".format(basic_id)

@route('/v1/longpassword')
def hello():
	basic_id_parts = []
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(secure_random.choice(prefixlist_international).capitalize())
	basic_id_parts.append("-")
	basic_id_parts.append(str(secure_random.randint(-1,upper_limit)).zfill(3))
	basic_id = "".join(basic_id_parts)
	return "{0}".format(basic_id)


run(host='0.0.0.0', port=80, debug=True)
