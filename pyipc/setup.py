from setuptools import setup, find_packages
setup(
name='pyipc',
version='0.1.0',
author='Zackary Morvan',
author_email='zackary.live8@gmail.com',
description='Inter-process communication library for Python3 to interact with JS renderer',
packages=find_packages(),
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