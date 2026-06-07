# -*- coding: utf-8 -*-
#
# setup.py
# SuperNanno
#
# Created by Heitor Bisneto on 2025.
# Copyright © 2025 hbisneto. All rights reserved.
#

from setuptools import setup, find_packages

# Ler o README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="supernanno",
    version="0.0.23",
    url="https://github.com/hbisneto/SuperNanno",
    license="BSD-3-Clause",
    
    author="Heitor Bardemaker A. Bisneto",
    author_email="bisnetoinc@gmail.com",
    
    description="Nano, but modern. A powerful terminal text editor built with Textual and Tree-sitter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    keywords=[
        "text-editor", "terminal", "tui", "editor", "nano", 
        "textual", "tree-sitter", "syntax-highlighting"
    ],
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Editors",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    python_requires=">=3.10",
    install_requires=[
        "textual==8.2.3",
        "rich==14.3.3",
        "tree-sitter==0.25.2",
        "tree-sitter-python==0.25.0",
        "tree-sitter-javascript==0.25.0",
        "tree-sitter-bash==0.25.1",
        "tree-sitter-rust==0.24.0",
        "tree-sitter-go==0.25.0",
        "tree-sitter-json==0.24.8",
        "tree-sitter-yaml==0.7.2",
        "tree-sitter-toml==0.7.0",
        "tree-sitter-markdown==0.5.1",
        "tree-sitter-html==0.23.2",
        "tree-sitter-css==0.25.0",
        "tree-sitter-java==0.23.5",
        "tree-sitter-sql==0.3.11",
        "tree-sitter-xml==0.7.0",
        "tree-sitter-regex==0.25.0",
        "Pygments==2.19.2",
        "httpx==0.28.1",
        "platformdirs==4.9.4",
        "markdown-it-py==4.0.0",
        "anyio==4.12.1",
        "linkify-it-py==2.1.0",
    ],
    
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.tcss", "*.md", "style.tcss"],
    },
    
    entry_points={
        "console_scripts": [
            "supernanno=supernanno.app:main",
        ],
    },
    
    project_urls={
        "Homepage": "https://hbisneto.github.io/SuperNanno",
        "Repository": "https://github.com/hbisneto/SuperNanno",
        "Bug Tracker": "https://github.com/hbisneto/SuperNanno/issues",
    },
)