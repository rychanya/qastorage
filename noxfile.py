import nox

nox.options.sessions = ["pretty"]


@nox.session(py=False)
def pretty(session: nox.Session):
    session.run("poetry", "run", "isort", ".")
    session.run("poetry", "run", "black", ".")
    session.run("poetry", "run", "flake8", ".")


@nox.session(py=False)
def tests(session: nox.Session):
    session.run("poetry", "run", "pytest")
