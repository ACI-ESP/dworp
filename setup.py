from setuptools import setup

__author__ = 'Cash Costello'
__email__ = 'cash.costello@jhuapl.edu'
__version__ = '0.1.0'

setup(
    name='dworp',
    version=__version__,
    description='Agent-based modeling framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__email__,
    url='https://github.com/ACI-ESP/dworp',
    license='BSD',
    packages=['dworp'],
    install_requires=[
        'numpy',
    ],
    extras_require={
        'plot': ['matplotlib']
    },
    python_requires='>=3.5',
    keywords='agents ABM modeling simulation agent-based',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Life'
    ],
)
