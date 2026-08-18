import json
import urllib.parse
from api.briefing import app as briefing_app


def app(environ, start_response):
    return briefing_app(environ, start_response)
