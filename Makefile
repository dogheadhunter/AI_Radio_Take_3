install:
	python -m venv .venv
	.venv\Scripts\pip install -r requirements.txt

test:
	.venv\Scripts\pytest -q

.PHONY: install test
