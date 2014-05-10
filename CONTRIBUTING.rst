============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given. 

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/tunnell/wax/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Be sure to also give enough context: depending on how severe the bug is,
it may be a while before somebody has time to fix the bug.  You should make
sure that the bug report is readable by somebody who is not the author and also
not familiar with problems you've been having.

Lastly, all bug reports must be in English since we view it as the
international language.  Please write in complete sentences and keep it
professional.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

We could always use more documentation, whether as part of the official docs,
in docstrings, or even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/tunnell/wax/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `wax` for local development.

0. Check that you have the following extra development packages installed::

    $ pip install flake8 tox sphinx sphinx_rtd_theme bumpversion

1. Fork the `wax` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/wax.git

3. Install your local copy into a virtualenv, as was recommended in the instructions.  This is how you set up your fork for local development::

    $ cd wax/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
tests, including testing other Python versions with tox::

    $ flake8 wax tests
	$ python setup.py test
    $ tox

It is important that you run these commands.  There is even a shortcut through
the Makefile to these commands: `make lint`, `make test`, `make test-all`.  If
you don't run these commands to ensure the tests pass, your changes will be
rejected to avoid trashing the repository for other people.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests of your new code.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3. Check
   https://travis-ci.org/tunnell/wax/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

	$ python -m unittest tests.test_wax

