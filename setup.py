from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='emailparser',
    version='0.0.1',
    description='Email Parsing Module',
    long_description=readme,
    author='Threat Lead',
    author_email='threatlead@gmail.com',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'samples')),
    install_requires=[
        'olefile',
        'pyunpack',
        'patool',
        'python-magic',
    ]
)
