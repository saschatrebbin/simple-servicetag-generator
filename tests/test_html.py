"""HTML escaping, presentation, and non-HTML regressions for V2 generators."""

import csv
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from test_identifier import app_module, get


class ResultParser(HTMLParser):
    """Capture the text and nested tags of generated result elements."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = {}
        self.children = {}
        self.tags = []
        self.buttons = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == 'button':
            self.buttons.append(attrs.get('onclick'))
        if self.current is not None:
            self.children[self.current].append(tag)
        element_id = attrs.get('id')
        if element_id and (element_id.startswith(('id-', 'long-', 'short-'))):
            self.current = element_id
            self.results[element_id] = ''
            self.children[element_id] = []
        elif tag == 'div' and attrs.get('class') == 'password':
            self.current = 'password'
            self.results['password'] = ''
            self.children['password'] = []

    def handle_data(self, data):
        if self.current is not None:
            self.results[self.current] += data

    def handle_endtag(self, tag):
        if self.current is not None and tag in ('div', 'span'):
            self.current = None


def parse(body):
    parser = ResultParser()
    parser.feed(body)
    return parser


class HtmlRenderingTests(unittest.TestCase):
    def test_templates_do_not_disable_html_escaping(self):
        template_dir = Path(__file__).resolve().parents[1] / 'app' / 'templates'
        templates = list(template_dir.rglob('*.tpl'))
        self.assertTrue(templates)
        for template in templates:
            with self.subTest(template=template):
                self.assertNotRegex(template.read_text(encoding='utf-8'), r'\{\{\s*!')

    def test_nanoid_single_and_multiple_escape_both_parameters_and_preserve_spaces(self):
        prefix = """  <script>alert('x')</script>&"  """
        suffix = """  '>&<img src=x onerror=alert(2)>  """
        for count in (1, 2):
            with self.subTest(count=count), mock.patch.object(
                app_module, '_nanoid_generate_one', side_effect=['ONE', 'TWO']
            ):
                status, headers, body = get(
                    '/api/v2/nanoid.html', {'count': count, 'prefix': prefix, 'suffix': suffix}
                )
            self.assertEqual(status, 200)
            self.assertIn('text/html', headers['Content-Type'])
            page = parse(body)
            self.assertEqual(page.results['id-0'], prefix + 'ONE' + suffix)
            if count == 2:
                self.assertEqual(page.results['id-1'], prefix + 'TWO' + suffix)
                self.assertIn('copyAllNano()', page.buttons)
                self.assertIn('copyOne(1)', page.buttons)
            self.assertIn('copyOne(0)', page.buttons)
            self.assertTrue(all(not child_tags for child_tags in page.children.values()))
            self.assertEqual(page.tags.count('script'), 1)  # The trusted clipboard script only.
            self.assertNotIn('img', page.tags)
            self.assertIn('white-space: pre-wrap', body)

    def test_identifier_values_remain_escaped_and_copy_buttons_exist(self):
        prefix = """  <b>&"'  """
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['alfa', 'bravo']):
            status, _, body = get('/v2/identifier.html', {
                'words': 1, 'numbers': 0, 'count': 2, 'prefix': prefix
            })
        self.assertEqual(status, 200)
        page = parse(body)
        self.assertEqual(page.results, {
            'long-0': prefix + 'Alfa', 'short-0': prefix + 'A',
            'long-1': prefix + 'Bravo', 'short-1': prefix + 'B'
        })
        self.assertTrue(all(not child_tags for child_tags in page.children.values()))
        self.assertNotIn('b', page.tags)
        self.assertIn("copyValue(0, 'both')", page.buttons)
        self.assertIn('copyAllIdentifiers()', page.buttons)
        self.assertIn('white-space: pre-wrap', body)

    def test_password_with_html_separator_is_not_interpreted_as_markup(self):
        with mock.patch.object(app_module.secrets, 'choice', side_effect=['alfa', 'bravo']):
            status, _, body = get('/api/v2/password.html', {
                'words': 2, 'numbers': 0, 'separator': '<'
            })
        self.assertEqual(status, 200)
        page = parse(body)
        self.assertEqual(page.results['password'], 'Alfa<Bravo')
        self.assertEqual(page.children['password'], [])
        self.assertIn('Alfa&lt;Bravo', body)

    def test_templates_work_from_an_unrelated_working_directory(self):
        old_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                app_module.bottle.TEMPLATES.clear()
                for path in ('/api/v2/nanoid.html', '/api/v2/identifier.html',
                             '/api/v2/password.html'):
                    with self.subTest(path=path):
                        self.assertEqual(get(path)[0], 200)
            finally:
                os.chdir(old_cwd)

    def test_nanoid_non_html_formats_keep_values_without_html_escaping(self):
        prefix, suffix, value = "  <&' ", ' >"  ', 'VALUE'
        expected = prefix + value + suffix
        for fmt in ('json', 'xml', 'csv', 'text'):
            with self.subTest(format=fmt), mock.patch.object(
                app_module, '_nanoid_generate_one', return_value=value
            ):
                status, _, body = get('/api/v2/nanoid.' + fmt, {
                    'prefix': prefix, 'suffix': suffix
                })
            self.assertEqual(status, 200)
            if fmt == 'json':
                result = json.loads(body)['ids'][0]
            elif fmt == 'xml':
                result = ET.fromstring(body).findtext('./ids/id')
            elif fmt == 'csv':
                result = list(csv.reader(io.StringIO(body)))[1][0]
            else:
                result = body.splitlines()[1]
            self.assertEqual(result, expected)

    def test_identifier_and_password_non_html_formats_keep_values(self):
        for fmt in ('json', 'xml', 'csv', 'text'):
            with self.subTest(endpoint='identifier', format=fmt), mock.patch.object(
                app_module.secrets, 'choice', return_value='alfa'
            ):
                status, _, body = get('/api/v2/identifier.' + fmt, {
                    'words': 1, 'numbers': 0, 'prefix': 'A<&'
                })
                self.assertEqual(status, 200)
                if fmt == 'json':
                    result = json.loads(body)['identifiers'][0]['long']
                elif fmt == 'xml':
                    result = ET.fromstring(body).findtext('./identifiers/identifier/long')
                elif fmt == 'csv':
                    result = next(csv.DictReader(io.StringIO(body)))['long']
                else:
                    result = body.split(' (')[0]
                self.assertEqual(result, 'A<&Alfa')
            with self.subTest(endpoint='password', format=fmt), mock.patch.object(
                app_module.secrets, 'choice', side_effect=['alfa', 'bravo']
            ):
                status, _, body = get('/api/v2/password.' + fmt, {
                    'words': 2, 'numbers': 0, 'separator': '<'
                })
                self.assertEqual(status, 200)
                if fmt == 'json':
                    result = json.loads(body)['password']
                elif fmt == 'xml':
                    result = ET.fromstring(body).findtext('./password')
                elif fmt == 'csv':
                    result = next(csv.DictReader(io.StringIO(body)))['password']
                else:
                    result = body
                self.assertEqual(result, 'Alfa<Bravo')


if __name__ == '__main__':
    unittest.main()
