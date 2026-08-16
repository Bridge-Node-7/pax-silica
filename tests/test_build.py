import hashlib, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BuildTests(unittest.TestCase):
    def test_deterministic_build(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",a],cwd=ROOT)
            subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",b],cwd=ROOT)
            def digest(root):
                root=Path(root); return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(digest(a),digest(b))
    def test_exact_public_artifact(self):
        with tempfile.TemporaryDirectory() as a:
            subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",a],cwd=ROOT)
            root=Path(a)
            observed={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            expected={"index.html","styles.css","app.js","data/pax-silica.json","data/sources.json","WEB_MANIFEST.sha256"}
            self.assertEqual(observed,expected)
if __name__=="__main__": unittest.main()
