from setuptools import setup, find_packages

setup(
    name="doc2ai",  # 改为 doc2ai
    version="1.0.0",
    description="Doc2AI - Convert documents to AI-friendly format",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pyyaml",
        "chardet",
        "pydantic",
        "aiofiles",
        "tiktoken",
        "python-docx",  # DOCX 支持
        "PyMuPDF",      # PDF 支持
    ],
    entry_points={
        "console_scripts": [
            "doc2ai=src.main:main",  # 命令改为 doc2ai
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)