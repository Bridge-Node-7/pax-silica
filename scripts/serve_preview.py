#!/usr/bin/env python3
import argparse, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument("--directory",required=True);ap.add_argument("--port",type=int,default=8765);args=ap.parse_args()
os.chdir(Path(args.directory))
ThreadingHTTPServer(("127.0.0.1",args.port),SimpleHTTPRequestHandler).serve_forever()
