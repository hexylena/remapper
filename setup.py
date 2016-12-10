from setuptools import setup


setup(
    name="redeclipse",
    version='0.0.1',
    description='RedEclipse / Cube2 / Saurbrauten map editor library',
    author='E. Rasche',
    author_email='hxr@hx42.org',
    install_requires=['enum34'],
    url='https://github.com/erasche/redeclipse-maps',
    packages=["redeclipse"],
    entry_points={
        'console_scripts': [
                'redeclipse_iso = redeclipse.cli.iso:main',
                'redeclipse_tojson = redeclipse.cli.to_json:main',
                'redeclipse_addtrees = redeclipse.cli.add_trees:main',
                'redeclipse_cfg = redeclipse.cli.cfg_gen:main',
            ]
        },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        ],
    include_package_data=True,
)
