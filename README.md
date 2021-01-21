# CsvPlotter

A simple to use script to plot CSV files using [matplotlib](https://matplotlib.org/).

## Current Features

- Print all column headers.
- Selectively plot columns. . This allows plotting any combination of columns.
- Reducing the amount of plotted samples by taking every n-th sample or specifying a range of samples to plot.

## (Maybe) Future Features

- Plotting different columns with an alternate Y-Axis.
- Multiple subplots in a single plot.
- Saving and restoring plot configurations in e.g. a YAML file for an easy reuse of common plotting setups.

## Installation

By now, the package is not yet published to the official PyPi. If you already want to use it you can install the package directly:

1. Clone this repo \
   `git clone git@github.com:skaupper/CsvPlotter-skaupper`
2. Install the required packages\
   `python3 -m pip install setuptools`
3. Install the package using *setuptools*\
   `python3 setup.py install`
