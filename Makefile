PIPENV := pipenv
PYTHON := $(PIPENV) run python
PACKAGE := dbpykitpw

.DEFAULT_GOAL := help

help:
	@echo "Targets:"
	@echo "  make install    Install package in development mode"
	@echo "  make sdist      Build source distribution"
	@echo "  make wheel      Build wheel only"
	@echo "  make build      Build sdist + wheel"
	@echo "  make demo       Publish demo files to current directory"
	@echo "  make demo-to    Publish demo files (usage: make demo-to OUTPUT=path)"
	@echo "  make clean      Remove build artifacts"
	@echo "  make uninstall  Uninstall package"

install:
	$(PIPENV) install -e .

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache

uninstall:
	$(PIPENV) run pip uninstall -y $(PACKAGE) || true

sdist:
	$(PYTHON) -m build --sdist

wheel:
	$(PYTHON) -m build --wheel

build: clean
	$(PYTHON) -m build
	$(PIPENV) run pip install dist/*.whl

demo:
	$(PYTHON) publish_demo.py -v

demo-to:
	$(PYTHON) publish_demo.py -o $(OUTPUT) -v

