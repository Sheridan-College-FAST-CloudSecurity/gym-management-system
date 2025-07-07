from setuptools import setup, find_packages

setup(
    name="gym_manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.23",
        "tabulate>=0.9.0",
        "python-dateutil>=2.8.2",
    ],
)