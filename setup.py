from setuptools import setup, find_packages

setup(
    name="eth-transaction-tracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.1.4",
        "python-dotenv>=1.0.0",
        "web3>=6.11.1",
        "eth-utils>=2.3.0",
    ],
    python_requires=">=3.9",
) 