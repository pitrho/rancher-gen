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
        print("Wrote coverage report to htmlcov directory")
        sys.exit(errno)


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('rancher_gen/__init__.py', 'rb') as f:
    __version__ = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='rancher-gen',
    version=__version__,
    description="File generator that renders templates using Rancher API",
    long_description=open('README.md', 'r').read(),
    author="Pit Rho Corporation",
    license="MIT",
    url="https://github.com/pitrho/rancher-gen",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'rancher-gen=rancher_gen.cli:main'
        ]
    },
    install_requires=[
        'Jinja2==2.8',
        'requests==2.11.1',
        'websocket-client==0.37.0'
    ],
    extras_require={},
    tests_require=[
        'tox==2.3.1'
    ],
    cmdclass={'test': PyTest}
)
