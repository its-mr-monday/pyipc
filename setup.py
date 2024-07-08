from setuptools import setup, find_packages
import os

with open('README.md', 'r') as f:
    long_description = f.read()
setup(
    name='pythonipc',
    version='1.3.2',
    author='itsmrmonday',
    author_email='zackary.live8@gmail.com',
    description='Inter-process communication library for Python3 to interact with JS renderer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/its-mr-monday/pyipc',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'flask',
        'flask_cors',
        'flask_socketio'
    ]
)