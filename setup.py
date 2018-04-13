from setuptools import setup

__author__ = 'Cash Costello'
__email__ = 'cash.costello@jhuapl.edu'
__version__ = '0.0.1.dev'

setup(
    name='dworp',
    version=__version__,
    description='Agent-based modeling frameowkr',
    long_description=open('README.md').read(),
    author=__author__,
    author_email=__email__,
    license='BSD',
    packages=['dworp'],
    keywords='',
    classifiers=[
    ],
    install_requires=[
        'numpy'
    ],
    python_requires='>=3.5',
)
