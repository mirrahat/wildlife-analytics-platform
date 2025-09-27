"""
Australian Biodiversity Platform Setup
======================================
Setup configuration for the Australian wildlife data collection platform.
"""

from setuptools import setup, find_packages

setup(
    name="australian-biodiversity-platform",
    version="1.0.0",
    description="Platform for collecting and analyzing Australian wildlife data",
    author="Wildlife Research Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "sqlite3",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aussie-wildlife=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
