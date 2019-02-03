"""
Setup for cnncalc

See setup.cfg for configuration
"""
from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'cnncalc = cnncalc.main:main',
        ],
    }
)



