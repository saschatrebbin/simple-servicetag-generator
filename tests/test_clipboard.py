"""Run the JavaScript clipboard tests as part of the Python test suite."""

from pathlib import Path
import shutil
import subprocess
import unittest


class ClipboardTests(unittest.TestCase):
    def test_shared_script_with_simulated_dom_and_clipboard(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required to run the clipboard tests')
        test_file = Path(__file__).resolve().with_name('clipboard.test.js')
        result = subprocess.run([node, '--test', str(test_file)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
