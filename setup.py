from setuptools import setup, find_packages

setup(
    name='rgcode',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['models']},
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        rgcode=rgcode.rgcode:main
        rgcode-gui=rgcode_gui.rgcode_gui:main
    ''',
)