import os
from glob import glob

from invoke import task

DOCS_PORT = os.environ.get("DOCS_PORT", 8000)


@task
def clean(c):
    """ Remove artifacts and binary files. """
    c.run("python setup.py clean --all")
    patterns = ["build", "dist"]
    patterns.extend(glob("*.egg*"))
    patterns.append("docs/_build")
    patterns.append("**/*.pyc")
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task
def lint(c):
    """ Run linting tox environments. """
    c.run("tox -epep8,isort,black,pypi-description")


@task  # NOQA
def format(c):  # NOQA
    """ Run code formatting tasks. """
    c.run("tox -eblacken,isort_format")


@task
def test(c):
    """ Run test in local environment. """
    c.run("python setup.py test")


@task
def test_all(c):
    """ Run all tox environments. """
    c.run("tox")


@task
def coverage(c):
    """ Run test with coverage in local environment. """
    c.run("coverage erase")
    c.run("run setup.py test")
    c.run("report -m")


@task
def tag_release(c, level):
    """ Tag release version. """
    c.run("bumpversion --list %s --no-tag" % level)


@task
def tag_dev(c, level="patch"):
    """ Tag development version. """
    c.run("bumpversion --list %s --message='Bump develop version [ci skip]' --no-tag" % level)


@task(pre=[clean])
def docbuild(c):
    """ Build documentation. """
    os.chdir("docs")
    c.run(f"python -msphinx -W -b html -d _build/doctrees . _build/html")


@task(docbuild)
def docserve(c):
    """Serve docs at http://localhost:$DOCS_PORT/ (default port is 8000)"""
    from livereload import Server

    server = Server()
    server.watch("docs/conf.py", lambda: docbuild(c))
    server.watch("CONTRIBUTING.rst", lambda: docbuild(c))
    server.watch("docs/*.rst", lambda: docbuild(c))
    server.serve(port=DOCS_PORT, root="_build/html")
