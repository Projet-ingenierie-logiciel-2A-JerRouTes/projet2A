from setuptools import find_packages, setup


setup(
    name="projet2a",
    version="0.1.0",
    packages=find_packages(where="src"),  # dit à setuptools de chercher dans src
    package_dir={"": "src"},  # le root des packages est src
    python_requires=">=3.13",
)
