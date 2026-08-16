.PHONY: check build preview

check:
	python scripts/check_repo.py

build:
	python scripts/build_web.py --output build/web

preview: build
	python scripts/serve_preview.py --directory build/web --port 8765
