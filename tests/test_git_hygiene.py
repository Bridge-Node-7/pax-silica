import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {'.md', '.py', '.json', '.html', '.css', '.js', '.yml', '.yaml', '.txt', '.lock', '.cff'}


class GitHygieneTests(unittest.TestCase):
    def test_text_files_have_no_trailing_whitespace_and_one_final_newline(self):
        offenders = []
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {'VERSION', 'NOTICE', 'LICENSE', 'Makefile', '.gitignore', '.gitattributes', '.editorconfig'}:
                continue
            raw = path.read_bytes()
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                offenders.append(f'{path.relative_to(ROOT)}: not UTF-8')
                continue
            lines = text.splitlines()
            for lineno, line in enumerate(lines, start=1):
                if line.rstrip(' \t') != line:
                    offenders.append(f'{path.relative_to(ROOT)}:{lineno}: trailing whitespace')
            if not text.endswith('\n') or text.endswith('\n\n'):
                offenders.append(f'{path.relative_to(ROOT)}: expected exactly one final newline')
        self.assertEqual(offenders, [], '\n'.join(offenders))


if __name__ == '__main__':
    unittest.main()
