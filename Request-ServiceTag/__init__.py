import logging

import azure.functions as func

import random
random_generator = random.SystemRandom()
prefixlist_international = ("alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "hotel", "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu")
upper_limit = 999
padding = 3

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    servicetag_parts = []
    servicetag_parts.append(random_generator.choice(prefixlist_international))
    servicetag_parts.append("-")
    servicetag_parts.append(str(random_generator.randint(-1,upper_limit)).zfill(3))
    servicetag = "".join(servicetag_parts)
    
    return func.HttpResponse(
            servicetag,
            status_code=200
    )