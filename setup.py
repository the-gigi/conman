from setuptools import setup

setup(name='conman',
      version='0.1',
      license='LICENSE',
      author='Gigi Sayfan',
      author_email='the.gigi@gmail.com',
      description='Manage configuration files',
      long_description=open('README.md').read(),
      zip_safe=False,
      setup_requires=['nose>=1.0'],
      test_suite='nose.collector')

