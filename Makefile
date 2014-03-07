.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
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

lint:
	flake8 --ignore=E501 cito tests

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source cito setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/cito.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ cito
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

	cp -r docs/_build/html/* ../citodocs/
	bash -c "cd ../citodocs;git add -A;git commit -m \"Generated gh-pages\";git push origin gh-pages;cd ../cito"

	echo open docs/_build/html/index.html

changelog:
	emacs -nw HISTORY.rst
	git commit -m "Update changelog" HISTORY.rst

major: clean docs changelog
	bumpversion major
	git push all
	git push all --tags
	python setup.py sdist upload

minor: clean docs changelog
	bumpversion minor
	git push all
	git push all --tags
	python setup.py sdist upload

patch: clean docs changelog
	bumpversion patch
	git push all
	git push all --tags
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist

profile: clean
	rm -f profile
	python cito/EventBuilder/Logic.py 