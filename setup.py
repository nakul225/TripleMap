import os
from setuptools import setup
from pip.req import parse_requirements

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]
setup(
	name = "TripleMap",
    version = "1",
    author = "Nakul Dhande",
    author_email = "nakul225@gmail.com",
    description = ("Triple map allows user to select particular \
	     position on Doublemap (Google Maps) and Triple Map would alert the \
	     user when the bus of his/her choice arrives at that point. This spares \
	     users to continuously monitor the Doublemap screen to check where the bus actually is."
    ),
    license = "MIT",
    keywords = "example documentation tutorial",
    url = "https://github.com/nakul225/TripleMap",
    install_requires = reqs,
    packages=['src'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
	)