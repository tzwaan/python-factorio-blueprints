from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py_factorio_blueprints',
    description='A python package to help create, '
                'modify and export factorio blueprints',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tzwaan/python-factorio-blueprints',
    author='Tijmen Zwaan',
    author_email='tijmen.zwaan@gmail.com',
    license='MIT',
    packages=[
        'py_factorio_blueprints'
    ],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)
