"""SVG structure, escaping and production CLI integration."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

from kira_frontend.ast_nodes import ASTNode
from kira_frontend.ast_svg import format_ast_svg

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://www.w3.org/2000/svg'}


class SVGTests(unittest.TestCase):
    def test_tree_structure_and_xml_escaping(self):
        tree = ASTNode('Program', (ASTNode('RelOp <', (
            ASTNode('Id left_with_a_long_name'), ASTNode('Int 3'),
        )), ASTNode('Id a&b')))
        svg = format_ast_svg(tree)
        root = ET.fromstring(svg)
        self.assertEqual(len(root.findall('.//s:path', NS)), 4)
        self.assertEqual({t.text for t in root.findall('.//s:text', NS)},
                         {'Program', 'RelOp <', 'Id left_with_a_long_name', 'Int 3', 'Id a&b'})
        self.assertEqual(svg, format_ast_svg(tree))
        self.assertEqual(tree.children[0].children[0].label, 'Id left_with_a_long_name')
        self.assertGreater(float(root.attrib['width']), 300)

    def test_cli_export_preserves_text_and_skips_invalid_input(self):
        with tempfile.TemporaryDirectory() as folder:
            svg = Path(folder) / 'tree.svg'
            valid = ROOT / 'tests/public/public1_arithmetic_if.kira'
            baseline = subprocess.run([sys.executable, str(ROOT/'kira.py'), str(valid)], capture_output=True)
            actual = subprocess.run([sys.executable, str(ROOT/'kira.py'), str(valid), '--svg', str(svg)], capture_output=True)
            self.assertEqual(actual.returncode, 0)
            self.assertEqual(actual.stdout, baseline.stdout)
            self.assertEqual(actual.stderr, baseline.stderr)
            ET.parse(svg)
            svg.unlink()
            for name in ('public4_lexical_errors.kira', 'public5_syntax_error.kira'):
                invalid = ROOT/'tests/public'/name
                failed = subprocess.run([sys.executable, str(ROOT/'kira.py'), str(invalid), '--svg', str(svg)], capture_output=True)
                self.assertEqual(failed.returncode, 1)
                self.assertFalse(svg.exists())

    def test_cli_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'case.kira'
            source.write_text('print(1);')
            result = subprocess.run([sys.executable, str(ROOT/'kira.py'), str(source), '--svg', str(source)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_text(), 'print(1);')
