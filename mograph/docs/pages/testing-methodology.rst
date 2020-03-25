Testing Methodology
===================

To ensure robustness and compliance with the requirements,
testing your software is vital. This project was built with
testability in mind.

The code was written in a modular fashion, so it's easier to test
its components separately.

Various strategies were implemented to make this step effective
and with minimal hassle.

TDD (Test Driven Development)
-----------------------------

This is actually the main development strategy I chose for this project.
Writing failing tests first, then implementing just enough to pass them has
been essential.

Here is why it was useful:

- Avoiding writing code that won't be needed after.
- Having a clear modular API for each component.
- Actually having tests that keep regression problems easily detectable.

The tests themselves use the `pytest` module, which is the de-facto standard
testing library for Python. Here's what a test looks like:

.. code-block:: python

    def test_graph_gen_basic(self):
        conf = {"mysql": {}, "app": {"deps": ["mysql"]}}

        g = config_to_graph(conf)
        g.validate()

        assert g.size() == 2
        assert g.has_consumer("mysql")
        assert g.has_consumer("app")

CI (Continuous Integration)
---------------------------

In addition to running the tests locally through the development cycle, I
wanted to have them running in a remote isolated environment too.

To do that, I integrated a "run tests" step in my `config.yaml` file. This
step was executed every I pushed code to Github.

It was especially useful for detecting errors related to the environment,
like "missing libraries", "file IO issues", etc...

Test Coverage
-------------

This was used as a supporting metric for the quality of the tests. Coverage
in and all by itself does not mean much if the tests are written just for
the sole purpose of maximizing coverage.

But when used properly, it can be a guide to "shine the light" on some parts
of the codebase that may have been overlooked.

Retrieving coverage reports was also integrated in the CI process through
`CodeCov <https://codecov.io/>`_.
