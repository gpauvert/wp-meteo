from distutils.core import setup

setup(
    name="wp-meteo",
    version="0.1.0",
    description="Python package to easily load exported WindPRO meteo text files into a pandas DataFrame.",
    url="https://github.com/gpauvert/wp-meteo",
    author="Guillaume Pauvert",
    author_email="g.pauvert@hotmail.com",
    keywords=["wind", "windpro"],
    license="gpl-3.0",
    packages=["wp_meteo"],
    install_requires=["pandas"]
)
