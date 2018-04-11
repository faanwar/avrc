import os
from subprocess import Popen, PIPE

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_chameleon',
    'zope.sqlalchemy',
    'sqlalchemy',
    'waitress',
    'Babel',
    'lingua',
    'avrc.redcross',
    'pyramid_ldap',
    'pyramid_rewrite'
    ]

extras_requires = {
    'test': [
        'nose', 'coverage', 'beautifulsoup4', 'WebTest', 'mock', 'ddt']
}

HERE = os.path.abspath(os.path.dirname(__file__))


def get_version():
    version_file = os.path.join(HERE, 'VERSION')

    # read fallback file
    try:
        with open(version_file, 'r+') as fp:
            version_txt = fp.read().strip()
    except:
        version_txt = None

    # read git version (if available)
    try:
        version_git = (
            Popen(['git', 'describe'], stdout=PIPE, stderr=PIPE, cwd=HERE)
            .communicate()[0]
            .strip())
    except:
        version_git = None

    version = version_git or version_txt or '0.0.0'

    # update fallback file if necessary
    if version != version_txt:
        with open(version_file, 'w') as fp:
            fp.write(version)

    return version


setup(
    name='aeh.earlytest',
    version=get_version(),
    description='Red Cross Web Site and Result Retrieval Application',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
    author='UCSD BIT Core',
    author_email='bitcore@ucsd.edu',
    license='BSD 2-clause "Simplified" License',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['aeh'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_requires,
    tests_require=extras_requires['test'],
    test_suite='nose.collector',
    entry_points="""\
    [paste.app_factory]
    main = aeh.earlytest:main
    """,
    message_extractors={'.': [
        ('**.py', 'lingua_python', None),
        ('**.pt', 'lingua_xml', None)]},
    )
