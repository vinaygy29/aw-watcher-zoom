.PHONY: build test package clean

build:
	poetry install

test:
	poetry run aw-watcher-zoom --help  # Ensures that it at least starts
	make typecheck

typecheck:
	poetry run mypy aw_watcher_zoom --ignore-missing-imports

package:
	pyinstaller aw-watcher-zoom.spec --clean --noconfirm

clean:
	rm -rf build dist
	rm -rf aw_watcher_zoom/__pycache__