from setuptools import setup, find_packages

setup(
    name="turbox",
    version="0.1.0",
    description="High-performance Python backend framework built on Codon",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "requests"],
    },
)
