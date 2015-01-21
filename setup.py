from setuptools import setup, find_packages

setup(
    name='django-formhelper',
    version='0.2',
    author='Ben Davis',
    author_email='bendavis78@gmail.com',
    url='http://github.com/bendavis78',
    description=('Django FormHelper is a collection of templates and '
                 'templatetags to ease the pain in building out web forms'),
    keywords='django forms',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages = find_packages(),
    include_package_data = True
)
