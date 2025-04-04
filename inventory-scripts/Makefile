.PHONY: all venv run clean

# default target, when make executed without arguments
all: install

$(VENV)/bin/activate: setup.py
	pyenv virtualenv 3.8.5 cli_setup
	pyenv activate cli_setup
	pip install --upgrade pip

install:
	pip3 install -e .

uninstall:
	pip3 uninstall cli_setup -y

# venv is a shortcut target
venv: $(VENV)/bin/activate

run: venv
	#./$(VENV)/bin/python3 app.py
	cli_skeleton

test: install
# 	cli_skeleton --help # Example test to run

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete