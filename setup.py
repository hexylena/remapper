from setuptools import find_packages, setup

with open('redeclipse/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

REQUIRES = [
    'enum34',
    'simplejson',
    'noise',
    'tqdm'
]

setup(
    name='redeclipse',
    version=version,
    description='RedEclipse / Cube2 / Saurbrauten map editor library',
    long_description=readme,
    author='E. Rasche',
    author_email='hxr@hx42.org',
    maintainer='E. Rasche',
    maintainer_email='hxr@hx42.org',
    url='https://github.com/erasche/redeclipse-maps',
    license='GPL-3.0',
    entry_points={
        'console_scripts': [
                'redeclipse_iso = redeclipse.cli.iso:main',
                'redeclipse_to_json = redeclipse.cli.to_json:main',
                'redeclipse_from_json = redeclipse.cli.from_json:main',
                'redeclipse_addtrees = redeclipse.cli.add_trees:main',
                'redeclipse_cfg = redeclipse.cli.cfg_gen:main',
                'redeclipse_voxel_1 = redeclipse.cli.voxel_1:main',
                'redeclipse_voxel_2 = redeclipse.cli.voxel_2:main',
                'redeclipse_voxel_3 = redeclipse.cli.voxel_3:main',
                'redeclipse_snow_forest = redeclipse.cli.snow_forest:main',
            ]
        },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console',
    ],
    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],
    include_package_data=True,
    packages=find_packages(),
)
