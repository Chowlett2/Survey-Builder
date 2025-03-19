from setuptools import setup, find_packages

setup(
    name="your-package-name",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'openai==1.25.1',
        'numpy==1.23.2',
        'setuptools>=58.0.0',
        'wheel>=0.36.0',
        'rich>=10.14.0',
        # Add any other dependencies here
    ],
    # Add any other metadata for your package
)
