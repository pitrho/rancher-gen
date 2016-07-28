import re
import ast
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest

        if self.pytest_args and len(self.pytest_args) > 0:
            self.test_args.extend(self.pytest_args.strip().split(' '))
            self.test_args.append('tests/')

        cov = coverage.Coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.report()
        cov.html_report()
        print "Wrote coverage report to htmlcov directory"
        sys.exit(errno)


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('rho_boilerplate_package/__init__.py', 'rb') as f:
    __version__ = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='rho-boilerplate-package',
    version=__version__,
    description="Pit Rho Boilerplate Package",
    long_description=open('README.md', 'r').read(),
    maintainer="Pit Rho Corporation",
    license="Commercial",
    url="https://bitbucket.org/pitrho/rho-boilerplate-package",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[],
    extras_require={},
    tests_require=[
        'coverage==4.0a5',
        'mock==1.0.1',
        'pytest==2.7.1'
    ],
    cmdclass={'test': PyTest}
)
