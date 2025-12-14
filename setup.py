from setuptools import setup, find_packages
from pathlib import Path

# Read README if exists
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="rahkaran-auth",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Authentication library for Rahkaran ERP system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rahkaran-auth",
    py_modules=["rahkaran_auth"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # Include JS files as package data
    package_data={
        "": ["*.js"],
    },
    include_package_data=True,
)
