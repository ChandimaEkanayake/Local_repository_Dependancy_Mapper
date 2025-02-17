import unittest
from core.dependency_analyzer import DependencyAnalyzer

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer(None)

    def test_analyze_imports(self):
        code = """
import os
import sys
from collections import defaultdict
"""
        expected = ['os', 'sys', 'collections']
        result = self.analyzer.analyze_dependencies(code)
        self.assertCountEqual(result, expected)

if __name__ == '__main__':
    unittest.main()