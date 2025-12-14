from setuptools import setup
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="rahkaran-auth",
    version="1.0.0",
    description="Authentication library for Rahkaran ERP system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmdmirh/Rahkaran_login_webservice",
    py_modules=["rahkaran_auth"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    # Include JS files
    data_files=[
        ("rahkaran_js", ["rsa_encrypt.js", "BigInt.js", "Barrett.js", "RSA.js"]),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
