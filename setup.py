from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py_factorio_blueprints',
    packages=['py_factorio_blueprints'],
    version='0.2.2',
    license='MIT',
    description='A python package to help create, '
                'modify and export factorio blueprints',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tijmen Zwaan',
    author_email='tijmen.zwaan@gmail.com',
    url='https://github.com/tzwaan/python-factorio-blueprints',
    download_url='https://github.com/tzwaan/python-factorio-blueprints/archive/v0.2.tar.gz',
    keywords=['factorio', 'blueprint'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Natural Language :: English'
    ],
    scripts=[],
    include_package_data=True,
    zip_safe=False)
