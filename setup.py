from setuptools import setup, find_packages

setup(
    name="autoclick",
    version="1.0.0",
    description="AutoClick - Desktop macro recorder for Linux & Windows",
    author="CrisTecnica",
    url="https://github.com/CrisTecnica/autoclick",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.6",
        "pynput>=1.8",
    ],
    entry_points={
        "console_scripts": [
            "autoclick=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
)
