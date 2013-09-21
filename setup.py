#!/usr/bin/env python

import os
from distutils.core import setup, Extension
import distutils.util

setup (name = 'pybanery',
       version= '1.0',
       description='Python interface for Kanbanery',
       author = 'Pablo Lluch',
       author_email = 'pablo.lluch@gmail.com',
       py_modules = ['pybanery'],
       scripts=['pybanery'],
)
