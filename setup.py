from setuptools import setup, find_packages

setup(
    name="plainchecker",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "openpyxl",
        "scikit-learn",
        "selenium",
        "click",
        "keyring",
        "tabulate",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "plainchecker=plainchecker.cli:plainchecker",
        ],
    },
)