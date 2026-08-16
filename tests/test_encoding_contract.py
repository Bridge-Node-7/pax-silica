import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class EncodingContractTests(unittest.TestCase):
    def test_text_file_io_is_explicit_utf8(self):
        offenders=[]
        for base in (ROOT/'scripts', ROOT/'tests'):
            for path in sorted(base.glob('*.py')):
                tree=ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    if node.func.attr not in {'read_text','write_text'}:
                        continue
                    has_encoding=any(k.arg=='encoding' for k in node.keywords)
                    if not has_encoding:
                        offenders.append(f'{path.relative_to(ROOT)}:{node.lineno}:{node.func.attr}')
        self.assertEqual(offenders, [], 'Text I/O must declare encoding="utf-8": ' + ', '.join(offenders))

if __name__ == '__main__':
    unittest.main()
