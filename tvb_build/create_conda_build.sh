#!/bin/bash

envname="tvb-run"

conda create -y -n $envname nomkl scipy numpy networkx scikit-learn cython h5py pip numexpr psutil ipython ipython-notebook

source activate $envname

conda install matplotlib pytables numba scikit-image pytest pytest-cov simplejson cherrypy sqlalchemy psycopg2 docutils

pip install tvb-gdist formencode cfflib genshi nibabel sqlalchemy-migrate allensdk BeautifulSoup4

# The next ones are for Mac build env:
# pip install py2app docutils apscheduler pyobjc
# pip install --upgrade setuptools
# pip install --upgrade distribute
# Edit python2.7/site-packages/macholib/MatchOGraph.py loader= into loader_path=
# Add an empty __init__.py in python2.7/site-packages/PyObjCTools/ folder or else py2app won't be able to process this module

# After these run "sh install_from_svn.sh" or "python setup.py develop/install" from each of TVB packages in the correct order

cd ..
sh install_from_svn.sh

conda uninstall pyside shiboken cairo

# python2.7/site-packages/matplotlib/mpl-data/matplotlibrc to Agg
