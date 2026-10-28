"""End-to-end tests for identifier and existing password routes, without a server."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults
import xml.etree.ElementTree as ET

APP_DIR = Path(__file__).resolve().parents[1] / 'app'
# The deployed image uses the installed Bottle package. Fall back to the
# vendored copy for offline runs; its imp.new_module needs a Python 3.12 shim.
if importlib.util.find_spec('bottle') is None:
    try:
        import imp  # noqa: F401
    except ImportError:
        imp = types.ModuleType('imp')
        imp.new_module = types.ModuleType
        sys.modules['imp'] = imp
    sys.path.insert(0, str(APP_DIR))
spec = importlib.util.spec_from_file_location('generator_app', APP_DIR / 'simple-servicetag-generator.py')
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


def get(path, params=None):
    environ = {}
    setup_testing_defaults(environ)
    environ['PATH_INFO'] = path
    environ['QUERY_STRING'] = urlencode(params or {})
    status_headers = {}

    def start_response(status, headers, exc_info=None):
        status_headers['status'] = int(status.split()[0])
        status_headers['headers'] = dict(headers)

    body_iter = app_module.bottle.default_app()(environ, start_response)
    try:
        body = b''.join(body_iter).decode('utf-8')
    finally:
        if hasattr(body_iter, 'close'):
            body_iter.close()
    return status_headers['status'], status_headers['headers'], body


class IdentifierTests(unittest.TestCase):
    def test_default_result_and_alias(self):
        for path in ('/v2/identifier.json', '/api/v2/identifier.json'):
            with self.subTest(path=path):
                status, headers, body = get(path)
                self.assertEqual(status, 200)
                self.assertIn('application/json', headers['Content-Type'])
                data = json.loads(body)
                self.assertEqual(data['count'], 1)
                item = data['identifiers'][0]
                words_and_number = item['long'].split('-')
                self.assertEqual(len(words_and_number), 6)
                self.assertEqual(len(words_and_number[-1]), 3)
                self.assertTrue(words_and_number[-1].isdigit())
                self.assertEqual(item['short'], ''.join(w[0].upper() for w in words_and_number[:-1]) + '-' + words_and_number[-1])

    def test_leading_zeroes_prefix_and_custom_separator(self):
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['delta', 'sierra']), \
             mock.patch.object(app_module.secrets, 'randbelow', return_value=7):
            status, _, body = get('/api/v2/identifier.json', {'words': 2, 'numbers': 3, 'separator': '_', 'prefix': 'CASE-'})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['identifiers'], [{'long': 'CASE-Delta_Sierra_007', 'short': 'CASE-DS_007'}])

    def test_without_numbers(self):
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['delta', 'sierra']):
            status, _, body = get('/v2/identifier.json', {'words': 2, 'numbers': 0})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['identifiers'][0], {'long': 'Delta-Sierra', 'short': 'DS'})

    def test_duplicate_short_form_is_regenerated(self):
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['alfa', 'alfa', 'bravo']):
            status, _, body = get('/v2/identifier.json', {'words': 1, 'numbers': 0, 'count': 2})
        self.assertEqual(status, 200)
        self.assertEqual([x['short'] for x in json.loads(body)['identifiers']], ['A', 'B'])

    def test_excessive_duplicate_draws_fail_cleanly(self):
        with mock.patch.object(app_module.secrets, 'choice', return_value='alfa') as choice:
            status, _, _ = get('/v2/identifier.json', {'words': 1, 'numbers': 0, 'count': 2})
        self.assertEqual(status, 503)
        self.assertLess(choice.call_count, 100000)

    def test_invalid_parameters(self):
        cases = [
            {'words': 'abc'}, {'words': 0}, {'words': 21},
            {'numbers': -1}, {'numbers': 21}, {'numbers': '1.5'},
            {'count': 0}, {'count': 1001}, {'count': 'oops'},
            {'separator': ''}, {'separator': 'ab'}, {'separator': 'a'},
            {'prefix': 'a' * 65},
            {'words': 1, 'numbers': 0, 'count': 27},
        ]
        for params in cases:
            with self.subTest(params=params):
                self.assertEqual(get('/v2/identifier.json', params)[0], 400)
        self.assertEqual(get('/v2/identifier.invalid')[0], 400)

    def test_text_and_csv_are_parseable(self):
        with mock.patch.object(app_module.secrets, 'choice', return_value='delta'), \
             mock.patch.object(app_module.secrets, 'randbelow', return_value=7):
            status, headers, text = get('/v2/identifier', {'words': 1})
            self.assertEqual(status, 200)
            self.assertIn('text/plain', headers['Content-Type'])
            self.assertEqual(text.strip(), 'Delta-007 (D-007)')
            status, headers, body = get('/v2/identifier.csv', {'words': 1, 'prefix': 'X,"'})
        self.assertEqual(status, 200)
        self.assertIn('text/csv', headers['Content-Type'])
        self.assertEqual(list(csv.DictReader(io.StringIO(body))), [{'long': 'X,"Delta-007', 'short': 'X,"D-007'}])

    def test_xml_round_trip(self):
        with mock.patch.object(app_module.secrets, 'choice', return_value='delta'), \
             mock.patch.object(app_module.secrets, 'randbelow', return_value=7):
            status, headers, body = get('/v2/identifier.xml', {'words': 1, 'prefix': 'A&B-'})
        self.assertEqual(status, 200)
        self.assertIn('application/xml', headers['Content-Type'])
        result = ET.fromstring(body).find('./identifiers/identifier')
        self.assertEqual(result.findtext('long'), 'A&B-Delta-007')
        self.assertEqual(result.findtext('short'), 'A&B-D-007')

    def test_html_escapes_user_input_and_offers_copy(self):
        status, headers, body = get('/v2/identifier.html', {'prefix': '<script>alert(1)</script>'})
        self.assertEqual(status, 200)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertNotIn('<script>alert(1)</script>', body)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', body)
        self.assertIn('clipboard', body)
        self.assertIn(".join('\\n')", body)

    def test_golf_present(self):
        self.assertIn('golf', app_module.prefixlist_international)
        self.assertEqual(len(app_module.prefixlist_international), 26)


class PasswordRegressionTests(unittest.TestCase):
    def test_password_route_existing_format_and_parameters(self):
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['delta', 'sierra']), \
             mock.patch.object(app_module.secrets, 'randbelow', return_value=7):
            status, _, body = get('/api/v2/password.json', {'words': 2, 'numbers': 3, 'separator': '_'})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {'password': 'Delta_Sierra_007'})

    def test_password_without_numbers(self):
        with mock.patch.object(app_module.secrets, 'choice', return_value='delta'):
            status, _, body = get('/v2/password', {'words': 1, 'numbers': 0})
        self.assertEqual((status, body), (200, 'Delta'))


if __name__ == '__main__':
    unittest.main()
