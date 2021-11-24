from setuptools import setup


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    lic = f.read()

setup(
    name="meteo",
    version="0.1.0",
    long_description=readme,
    url="https://github.com/gpauvert/meteo",
    license=lic,
    packages=["meteo"],
    install_requires=["pandas"]
)
