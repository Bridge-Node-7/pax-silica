import subprocess, sys, tempfile, unittest, re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.h1=0
        self.main=0
        self.refs=[]

    def handle_starttag(self,t,a):
        d=dict(a)
        if "id" in d:
            self.ids.append(d["id"])
        if t=="h1":
            self.h1+=1
        if t=="main":
            self.main+=1
        for k in ("href","src"):
            if d.get(k):
                self.refs.append(d[k])

class HtmlTests(unittest.TestCase):
    def test_html_contract(self):
        with tempfile.TemporaryDirectory() as a:
            subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",a],cwd=ROOT)
            text=(Path(a)/"index.html").read_text(encoding="utf-8")
            p=P();p.feed(text)
            self.assertEqual(p.h1,1)
            self.assertEqual(p.main,1)
            self.assertEqual(len(p.ids),len(set(p.ids)))
            self.assertRegex(
                text,
                r'<link\b(?=[^>]*rel="canonical")(?=[^>]*href="https://bridgenode7\.com/pax-silica/")[^>]*>'
            )
            self.assertRegex(
                text,
                r'<meta\b(?=[^>]*name="robots")(?=[^>]*content="index,follow")[^>]*>'
            )
            self.assertNotIn("{{",text)

if __name__=="__main__":
    unittest.main()
