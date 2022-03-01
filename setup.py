from setuptools import setup
with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()
setup(
   name = 'pyMZML',
   author = 'gkreder',
   description = 'mzML parsing in Python',
   version = '0.1.0',
   packages = ['pyMZML'],
   install_requires = [req for req in requirements if req[:2] != "# "],
   include_package_data=True,
   entry_points = {
      'console_scripts': [
         'docopt = pyMZML.pyMZML:main'
      ]
   }
)