
from setuptools import setup, find_packages

README = open('README.md', 'r').read()

setup(
    name='joycontrol-pluginloader-ex',
    version='0.4a',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/null-Y-K/joycontrol-pluginloader',
    author='null-Y-K',
    description='PluginLoader Ex for mart1nro/joycontrol, Almtr/joycontrol-pluginloader',
    packages=find_packages(),
    install_requires=[
        'hid', 'aioconsole', 'dbus-python', 'crc8', 'pygame',
    ],
    entry_points={
        'console_scripts': [
            'joycontrol-pluginloader=JoycontrolPlugin.loader:main',
        ],
    },
)
