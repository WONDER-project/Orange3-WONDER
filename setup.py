#!/usr/bin/env python3

import io
import os

from setuptools import setup, find_packages

with io.open('about.md', 'r', encoding='utf-8') as f:
    ABOUT = f.read()

NAME = 'Orange3-WONDER-1'

MAJOR = 1
MINOR = 0
MICRO = 4
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

AUTHOR = 'Luca Rebuffi, Paolo Scardi, Alberto Flor'
AUTHOR_EMAIL = 'paolo.scardi@unitn.ut'

URL = 'https://github.com/WONDER-project/Orange3-WONDER'
DESCRIPTION = 'Whole POwder PatterN MoDEl in Orange.'
LONG_DESCRIPTION = ABOUT
LICENSE = 'GPL3+'

CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3 :: Only'
]

KEYWORDS = [
    'orange3 add-on',
    'orange3-wonder-1'
]

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.wonder.view.wonder'        : ['icons/*.*', 'data/*.*'],
    'orangecontrib.wonder.controller.fit.data': ['*.*', 'delta_l_files/*.*'],
}

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))) - {''})

ENTRY_POINTS = {
    'orange.widgets':
        ('Wonder 1 = orangecontrib.wonder.view.wonder',
         ),
    'orange3.addon':
        ('Orange3-WONDER-1 = orangecontrib.wonder',)



}

from distutils.core import setup

if __name__ == '__main__':

    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        namespace_packages=['orangecontrib'],
        #namespace_packages=NAMESPACE_PACAKGES,
        entry_points=ENTRY_POINTS
    )
