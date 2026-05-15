.PHONY: test lint coverage install clean

install:
	poetry install

test:
	poetry run pytest -v

coverage:
	poetry run pytest --cov=apolo_11 --cov-report=term-missing

lint:
	poetry run flake8 apolo_11/ tests/

format:
	poetry run autopep8 --in-place --recursive apolo_11/ tests/

clean:
	rm -rf htmlcov .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
