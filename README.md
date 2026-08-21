# RGCode
RGCode (Retinal Ganglion Cell quantification based On DEep learning) is a deep learning pipeline for automatic retinal segmentation and RGC counting.

## Changes since initial release
To see what's changed in new versions since the initial [publication](https://www.nature.com/articles/s41598-020-80308-y), check out the [release notes](doc/release.md)

## Installation
We recommend installing all the required dependencies through [Miniconda](https://docs.conda.io/en/latest/miniconda.html), allowing RGCode to run inside a dedicated environment without interfering or causing conflicts with the host computer.

All the required libraries are specified in the [rgcode.yml](rgcode.yml) file and a dedicated environment can be created running the following commands within Anaconda Prompt (on Windows) or a terminal on Linux and macOS.
NOTE: all the following commands should be run from within the RGCode folder

    (base) $ conda env create -f rgcode.yml
    (base) $ conda activate rgcode
    (rgcode) $ pip install .

For a more detailed installation guide, check out [this tutorial](doc/Tutorial_RGCode.pdf)

## Usage
RGCode can be run from a terminal, after activating the rgcode environment, by simply running rgcode

    (base) $ conda activate rgcode
    (rgcode) $ rgcode

Help on the parameters needed to run RGCode can be visualized by running

    (rgcode) $ rgcode --help

For a more detailed usage guide, check out [this tutorial](doc/Tutorial_RGCode.pdf)

### Graphical interface
Most of the RGCode functionality is also included in a user-friendly graphical interface, which can be launched with the command below

    (rgcode) $ rgcode-gui

### Training
Models based on RGCode can be trained using the scripts and following the instructions at [rgcode-train](https://gitlab.com/NCDRlab/rgcode-train).