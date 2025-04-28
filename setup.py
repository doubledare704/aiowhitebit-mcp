"""Setup script for aiowhitebit-mcp package.

This module contains the setup configuration for installing the aiowhitebit-mcp
package, which provides an MCP server and client for the WhiteBit cryptocurrency
exchange API.
"""

from setuptools import find_packages, setup

# Define development requirements
development_requires = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.23.5",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.4",
    "pyright>=1.1.355",
    "pre-commit>=3.6.2",
]

setup(
    name="aiowhitebit-mcp",
    version="0.2.2",
    description="MCP server and client for WhiteBit cryptocurrency exchange API",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/aiowhitebit-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiowhitebit==0.2.0",
        "fastmcp==2.2.5",
    ],
    entry_points={
        "console_scripts": [
            "aiowhitebit-mcp=aiowhitebit_mcp.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    extras_require={
        "dev": development_requires,
    },
)
