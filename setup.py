from setuptools import setup, find_packages
import os

dir = os.path.dirname(__file__)
readme = os.path.join(dir, 'README.rst')

setup(
    name='django-formhelper',
    version='0.1',
    author='Ben Davis',
    author_email='code@bendavismedia.com',
    url='http://github.com/bendavis78/django-form-helper',
    description=('Django FormHelper is a collection of templates and '
                 'templatetags to ease the pain in building out web forms'),
    keywords='django forms',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages = find_packages(),
    include_package_data = True,
    long_description=open(readme).read()
)
