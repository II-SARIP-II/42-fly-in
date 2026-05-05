FLK 	:= flake8
MYPY 	:= mypy
FLAGS	:= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv add pydantic pygame-ce

uninstall:
	pip uninstall pydantic pygame-ce

run:
	@python -m src maps/challenger/01_the_impossible_dream.txt

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
	$(MYPY) . $(FLAGS) --strict

init:
	uv init

venv:
	uv venv

.PHONY: install, uninstall, run, debug, clean, lint, lint-strict, init, venv
