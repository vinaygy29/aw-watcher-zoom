build:
	poetry install
	
package:
	pyinstaller aw-watcher-zoom.spec --clean --noconfirm