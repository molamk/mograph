Continuous Integration
======================

To have a robust development workflow, `Continuous Integration <https://codeship.com/continuous-integration-essentials>`_
is essential. The CI vendor for this project is `CircleCI <https://circleci.com/>`_.

This gives us an isolated, reproducible environment, in which we run multiple steps:

1. Checkout the codebase
2. Install the project's dependencies
3. Run the test suite
4. Collect testing coverage
5. Send the coverage results to `CodeCov <https://codecov.io/>`_
6. If any of the steps fail, all fails & an email is sent

Pipeline Specification
----------------------

Here's the actual CircleCI pipeline configuration:

.. code-block:: yaml

    version: 2.1

    orbs:
    python: circleci/python@0.2.1

    jobs:
    build-and-test:
        executor: python/default
        steps:
        - checkout
        - python/load-cache
        - python/install-deps
        - python/save-cache
        - run:
            command: python -m pytest --cov=mograph
            name: Test
        - run:
            command: python -m coverage html
            name: Generate HTML Coverage Report
        - store_test_results:
            path: htmlcov
        - store_artifacts:
            path: htmlcov
            destination: tr1
        - run:
            command: python -m codecov
            name: Upload Coverage Report

    workflows:
    main:
        jobs:
        - build-and-test
