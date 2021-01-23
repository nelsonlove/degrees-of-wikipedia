from setuptools import setup

setup(
   name='degrees_of_wikipedia',
   version='0.0.1',
   description='Simple Wikipedia game à la Seven Degrees of Kevin Bacon',
   author='Nelson Love',
   author_email='nelson.love@me.com',
   packages=['degrees_of_wikipedia'],
   install_requires=['bs4', 'flask', 'requests'], #external packages as dependencies
)
