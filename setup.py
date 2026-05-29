from setuptools import setup, find_packages

setup(
    name="supernanno",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "supernanno=app:main"
        ]
    }
)