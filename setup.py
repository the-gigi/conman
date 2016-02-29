from setuptools import setup, find_packages

setup(name='conman',
      version='0.3',
      url='https://github.com/the-gigi/conman',
      license='MIT',
      author='Gigi Sayfan',
      author_email='the.gigi@gmail.com',
      description='Manage configuration files',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False,
      setup_requires=['nose>=1.0'],
      test_suite='nose.collector')

