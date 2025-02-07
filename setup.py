# setup.py
from setuptools import setup

setup(
    name="PDFFiller",
    version="1.0",
    packages=[""],
    install_requires=[
        "flask",
        "pdfplumber",
        "reportlab",
        "PyPDF2"
    ]
)