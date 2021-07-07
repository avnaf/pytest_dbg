from setuptools import setup

setup(
    name='pytest_dbg',
    packages=['src'],
    install_requires=[
        'ipdb',
        'pudb',
    ],
    entry_points={'pytest11': ['pytest_dbg = src.plugin']},
    python_requires='>=3.5',
    version='0.1',
)
