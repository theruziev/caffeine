from distutils.core import setup

from setuptools import find_packages
from caffeine import app_info
setup(
    name=app_info.name,
    version=app_info.version,
    packages=find_packages(),
    url='https://github.com/theruziev/caffeine',
    license='MIT',
    author='Bakhtiyor Ruziev',
    author_email='bakhtiyor.ruziev@yandex.ru',
    description=''
)
