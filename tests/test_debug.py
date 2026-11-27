"""Tests for APP_DEBUG at startup and the resulting HTTP error responses."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


APP_PATH = Path(__file__).resolve().parents[1] / 'app' / 'simple-servicetag-generator.py'

# Match the existing tests: use the installed Bottle package when available,
# otherwise load the vendored snapshot with the Python 3.12+ imp shim.
BOOTSTRAP = r'''
import importlib.util
from pathlib import Path
import sys
import types

if importlib.util.find_spec('bottle') is None:
    try:
        import imp
    except ImportError:
        imp = types.ModuleType('imp')
        imp.new_module = types.ModuleType
        sys.modules['imp'] = imp
    sys.path.insert(0, str(Path(sys.argv[1]).parent))
import bottle
'''

STUBBED_START = BOOTSTRAP + r'''
import json
import runpy
from unittest.mock import patch

def capture_run(**kwargs):
    print(json.dumps({'debug': kwargs['debug'], 'type': type(kwargs['debug']).__name__,
                      'host': kwargs['host'], 'port': kwargs['port']}))

with patch.object(bottle, 'run', side_effect=capture_run):
    runpy.run_path(sys.argv[1], run_name='__main__')
'''

REAL_START = BOOTSTRAP + r'''
import runpy
runpy.run_path(sys.argv[1], run_name='__main__')
'''


def app_env(debug_value, port='3000'):
    env = os.environ.copy()
    env.update(APP_IP='127.0.0.1', APP_PORT=port)
    if debug_value is None:
        env.pop('APP_DEBUG', None)
    else:
        env['APP_DEBUG'] = debug_value
    return env


class DebugStartupTests(unittest.TestCase):
    def test_startup_passes_explicit_boolean_for_supported_values(self):
        cases = [
            (None, False), ('', False), ('  ', False), ('false', False),
            ('0', False), ('no', False), ('off', False), ('  FaLsE  ', False),
            ('true', True), ('1', True), ('yes', True), ('on', True),
            ('  TrUe  ', True),
        ]
        for value, expected in cases:
            with self.subTest(APP_DEBUG=value):
                result = subprocess.run(
                    [sys.executable, '-c', STUBBED_START, str(APP_PATH)],
                    env=app_env(value, port='3123'), capture_output=True,
                    text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                actual = json.loads(result.stdout)
                self.assertEqual(actual['type'], 'bool')
                self.assertIs(actual['debug'], expected)
                self.assertEqual(actual['host'], '127.0.0.1')
                self.assertEqual(actual['port'], '3123')

    def test_invalid_values_fail_before_server_start(self):
        for value in ('tru', 'disabled', '2'):
            with self.subTest(APP_DEBUG=value):
                result = subprocess.run(
                    [sys.executable, '-c', STUBBED_START, str(APP_PATH)],
                    env=app_env(value), capture_output=True, text=True, timeout=10,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('APP_DEBUG', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_http_errors_do_not_expose_tracebacks_when_debug_is_disabled(self):
        for value in (None, 'false'):
            with self.subTest(APP_DEBUG=value):
                status, body = self._request_error(value)
                self.assertEqual(status, 500)
                self.assertNotIn('Traceback (most recent call last)', body)
                self.assertNotIn('ValueError', body)

    def test_debug_can_be_intentionally_enabled(self):
        status, body = self._request_error('true')
        self.assertEqual(status, 500)
        self.assertIn('Traceback (most recent call last)', body)
        self.assertIn('ValueError', body)

    def _request_error(self, debug_value):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = str(sock.getsockname()[1])

        process = subprocess.Popen(
            [sys.executable, '-c', REAL_START, str(APP_PATH)],
            env=app_env(debug_value, port), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
        try:
            base = f'http://127.0.0.1:{port}'
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    stdout, stderr = process.communicate(timeout=5)
                    self.fail(f'Server exited before becoming ready: {stdout}\n{stderr}')
                try:
                    with urlopen(base + '/health', timeout=0.5) as response:
                        self.assertEqual(response.status, 200)
                    break
                except (URLError, TimeoutError, ConnectionError):
                    time.sleep(0.05)
            else:
                self.fail('Server did not become ready')

            with self.assertRaises(HTTPError) as response:
                urlopen(base + '/v2/password?words=not-a-number', timeout=5)
            try:
                return response.exception.code, response.exception.read().decode('utf-8')
            finally:
                response.exception.close()
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)


if __name__ == '__main__':
    unittest.main()
