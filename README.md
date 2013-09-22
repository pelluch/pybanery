pybanery
=========

Python command line interface for kanbanery.

Requirements
=========

* python >= 2.7, including versions 3 and above : http://www.python.org/download/releases/3.3.2
* python requests library : http://docs.python-requests.org/en/latest
* pycrypto >= 2.6 : https://www.dlitz.net/software/pycrypto
* simple-crypt >= 1.0.0 : https://pypi.python.org/pypi/simple-crypt

The three above may be installed with pip. Further instructions:

1.  If easy_install is not available:
	* Most likely windows, install appropriate version from http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools

2.  If pip is not available: Run easy_install pip

3.  Run pip install requests pycrypto simple-crypt

NOTE: This package is compatible with both python 2.x and python 3.x, but make sure to use the
same version of pip/easy_install to install all packages.

Usage
=========

The package can be installed with

	python setup.py build
	python setup.py install

To use, simply run the pybanery script from command line. If no args are passed, a menu will show available options.
To see available command line arguments:

	pybanery -h
