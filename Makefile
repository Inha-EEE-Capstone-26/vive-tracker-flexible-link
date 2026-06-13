PYTHON ?= python

.PHONY: verify smoke test

verify:
	$(PYTHON) scripts/verify_package.py

smoke: verify

test:
	$(PYTHON) -m unittest discover -s tests
