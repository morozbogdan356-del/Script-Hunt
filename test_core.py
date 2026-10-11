import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import build, check
from services.analyzer import analyze, repair

class CoreTests(unittest.TestCase):
    def test_generation(self):
        code, modules=build('сделай fly speed esp')
        self.assertEqual(set(modules), {'fly','speed','highlight'})
        self.assertTrue(check(code)[0])
    def test_unknown_request(self):
        self.assertIsNone(build('создай совершенно новую механику')[0])
    def test_risk_detection(self):
        self.assertIn('удалённая загрузка кода', analyze('loadstring(foo)'))
    def test_repair_whitespace(self):
        self.assertEqual(repair('hello  \r\n'), 'hello\n')
    def test_user_data_isolation(self):
        with tempfile.TemporaryDirectory() as td:
            from services import storage
            with patch.object(storage, 'DB', Path(td)/'test.sqlite3'):
                sid=storage.save(111, 'Test','print("hi")')
                self.assertIsNone(storage.get(222,sid))
                self.assertEqual(storage.get(111,sid)[0], 'Test')
                storage.set_language(111,'uk')
                self.assertEqual(storage.language(111),'uk')

if __name__ == '__main__': unittest.main()
