from setuptools import setup, find_packages

setup(
    name="supernanno",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "supernanno=app:main"
        ]
    }
)