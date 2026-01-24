install:
	python -m venv .venv
	.venv\Scripts\pip install -r requirements.txt

test:
	.venv\Scripts\pytest -q

test-mock:
	@echo "Running mock tests (fast)..."
	set TEST_MODE=mock && .venv\Scripts\pytest -q

test-integration:
	@echo "Running integration tests (requires services)..."
	set TEST_MODE=integration && .venv\Scripts\pytest -q

test-all:
	@echo "Running all tests including integration..."
	set TEST_MODE=integration && .venv\Scripts\pytest -v

.PHONY: install test test-mock test-integration test-all
