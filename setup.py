from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    my_license = f.read()

setup(
    name='psychup',
    version='0.1.0',
    description='Joker malware related tweets detection',
    long_description=readme,
    author='Adriana Luntraru',
    author_email='adriana.luntraru@gmail.com',
    url='https://github.com/adriana44/PsychUp',
    license=my_license,
    packages=find_packages()
)
