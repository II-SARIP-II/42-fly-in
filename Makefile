FLK 	:= flake8
MYPY 	:= mypy
FLAGS	:= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv add pydantic numpy

uninstall:
	pip uninstall pydantic numpy

run:
	@python -m src maps/medium/02_circular_loop.txt

debug:
	uv run python -m pdb src/__main__.py

clean:
	rm -rf __pycache__ .mypy_cache .python-version .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +


lint:
	$(FLK) . --extend-exclude .venv
	$(MYPY) . $(FLAGS)

lint-strict:
	$(FLK) . --extend-exclude .venv
	$(MYPY) . --strict

init:
	uv init

venv:
	uv venv

del-venv:
	rm -rf callmemaybe

.PHONY: install, uninstall, run, debug, clean, lint, lint-strict, init, venv
