from setuptools import setup, find_packages

NAME = 'golr-schema-generator'
DESCRIPTION = 'GOlr Schema Generator'
URL = 'https://github.com/deepakunni3/golr-schema-generator'
AUTHOR = 'Deepak Unni'
EMAIL = 'deepak.unni3@gmail.com'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = '0.0.1'
LICENSE = 'BSD3'

REQUIRED = [
    'PyYAML>=5.3'
]

EXTRAS = {
    'test': ['pytest']
}


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    license=LICENSE,
    packages=find_packages(),
    keywords='Solr GOlr golr-schema',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True
)