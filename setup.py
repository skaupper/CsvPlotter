import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='csv-plotter-skaupper',
    version='0.0.2',
    author='Sebastian Kaupper',
    author_email='kauppersebastian@gmail.com',
    description='A simple to use CSV plotter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/skaupper/CsvPlotter',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

    entry_points={
        'console_scripts': [
            'csv_plot=CsvPlotter.entrypoints:plot',
            'csv_util=CsvPlotter.entrypoints:util',
            'csv_transform=CsvPlotter.entrypoints:transform'
        ]
    },
    install_requires=[
        'numpy>=1.15.0',
        'matplotlib>=3.0.0',
        'pyyaml>=5.1'
    ]
)
