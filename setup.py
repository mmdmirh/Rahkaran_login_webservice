from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="rahkaran-auth",
    version="1.0.1",
    description="Authentication library for Rahkaran ERP system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmdmirh/Rahkaran_login_webservice",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    # Include JS files in the package
    package_data={
        "rahkaran_auth": ["*.js"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
