from setuptools import setup

setup(name='dataprov',
      version='0.1',
      description='Automatic provenance metadata creator',
      url='...',
      author='Felix Bartusch',
      author_email='felix.bartusch@uni-tuebingen.de',
      license='TODO',
      packages=['dataprov'],
      entry_points = {
          'console_scripts': ['dataprov=dataprov.dataprov:main']
      },
      install_requires=[
          'argparse',
          'lxml'
      ],
      include_package_data=True,
      zip_safe=False)

