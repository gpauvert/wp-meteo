from setuptools import setup


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    lic = f.read()

setup(
    name="wp-meteo",
    version="0.1.0",
    long_description=readme,
    url="https://github.com/gpauvert/wp-meteo",
    author="Guillaume Pauvert",
    author_email="g.pauvert@hotmail.com",
    license=lic,
    packages=["wp_meteo"],
    install_requires=["pandas"]
)
