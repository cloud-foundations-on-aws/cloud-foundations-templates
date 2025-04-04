from setuptools import setup

setup(
    name='cli_skeleton',        # Update Name
    packages=['cli_skeleton'],  # Name of CLI
    version='0.1.0',            # Version
    description='A cli for X',  # Description
    author='NAME',              # Author
    url='https://github.com/REPO',  # To be updated
    author_email='NAME@EMAIL.com',  # Email
    download_url='https://github.com/REPO',  # To be updated
    keywords=['aws', 'python'],  # Key words for cli
    classifiers=[],
    install_requires=[
        "PACKAGE"               # Add all packages
        ],
    setup_requires=[],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'cli_skeleton = cli_skeleton.__main__:main',
            ],
        },
    )
