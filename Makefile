.PHONY: check build preview watch

check:
	python scripts/check_repo.py

build:
	python scripts/build_web.py --output build/web

preview: build
	python scripts/serve_preview.py --directory build/web --port 8765

watch:
	python scripts/intelligence_watch.py --as-of 2026-08-15 --warn-days 2
