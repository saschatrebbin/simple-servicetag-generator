import random

secure_random = random.SystemRandom()

prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
upper_limit = 999
padding = 3

basic_id_parts = []
basic_id_parts.append(secure_random.choice(prefixlist_international))
basic_id_parts.append("-")
basic_id_parts.append(str(secure_random.randint(-1,upper_limit)).zfill(3))
basic_id = "".join(basic_id_parts)

print(basic_id)