venv:
	python3.10 -m venv .venv
	echo 'run `source .venv/bin/activate` to start using the virtual environment'

install:
	pip install wheel==0.42.0
	pip install -e .

distclean:
	rm -rf .venv
