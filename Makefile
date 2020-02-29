default:
	python3 main.py

mypy:
	# Or use --strict, a superset of --disallow-untyped-defs
	mypy --config-file mypy.ini --disallow-untyped-defs *.py

pylint:
	pylint --rcfile=pylintrc *.py

profile:
	python3 -m profile -s cumtime main.py

clean:
	rm -fr __pycache__
	rm -fr .mypy_cache
	rm -fr venv