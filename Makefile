FLK 	:= flake8
MYPY 	:= mypy
FLAGS	:= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv add pydantic numpy

uninstall:
	pip uninstall pydantic numpy

run:
	@uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json

debug:
	uv run python -m pdb src/__main__.py

clean:
	rm -rf __pycache__ .mypy_cache .python-version llm_sdk/.mypy_cache llm_sdk/__pycache__ .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +


lint:
	$(FLK) . --extend-exclude .venv,llm_sdk
	$(MYPY) . $(FLAGS)

lint-strict:
	$(FLK) . --extend-exclude .venv,llm_sdk
	$(MYPY) . --strict

init:
	uv init

venv:
	uv venv

del-venv:
	rm -rf callmemaybe

.PHONY: install, uninstall, run, debug, clean, lint, lint-strict, init, venv
