.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "develop - tell virtual env to run from here"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "major - tag, push, package and upload a major release"
	@echo "minor - tag, push, package and upload a minor release"
	@echo "patch - tag, push, package and upload a patch release"
	@echo "profile - profile the code and put results in file called profile"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:	clean
	flake8 --ignore=E501 wax tests

install: clean
	python setup.py install

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source wax setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/wax.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ wax
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

	cp -r docs/_build/html/* ../waxdocs/
	bash -c "cd ../waxdocs;git add -A;git commit -m \"Generated gh-pages\";git push origin gh-pages;cd ../wax"

	echo open docs/_build/html/index.html

major: clean docs
	bumpversion major
	git push
	git push --tags
	#python setup.py sdist upload

minor: clean docs
	bumpversion minor
	git push
	git push --tags
	#python setup.py sdist upload

patch: clean docs
	bumpversion patch
	git push
	git push --tags
	#python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist

profile: clean
	rm -f profile
	python wax/event-builder --profile