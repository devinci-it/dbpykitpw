"""
Setup configuration for dbpykitpw package.
Provides installation, distribution, and command-line tools.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long_description
def read_file(filename):
    """Read and return file contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


# Read the version from a version file or hardcode it
__version__ = '1.0.0'


setup(
    name='dbpykitpw',
    version=__version__,
    author='devinci-it',
    description='Database Python Kit with Peewee and Workflows',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/devinci-it/dbpykitpw',
    license='MIT',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    
    python_requires='>=3.8',
    install_requires=[
        'peewee>=3.14.0',
    ],
    
    extras_require={
        'dev': [
            'build>=0.9.0',
            'wheel>=0.37.0',
            'setuptools>=65.0.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'dbpykitpw=dbpykitpw.cli.console:main'
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
    ],
    
    keywords='database orm peewee repository pattern',
)
