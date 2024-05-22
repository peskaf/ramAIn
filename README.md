# RamAIn

Raman microspectroscopy data processing app

# Installation

## Windows
  1. Run `pip install -r requirements.txt`,
  2. run `python main.py`

If you want to make executable file, run `pyinstaller main.spec`.
This can be later used for example for [making distributable app installer](https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/) (e.g. using [ForgeInstaller](https://installforge.net/)). NOTE: when trying the built exe file in dist directory, there may be bug that some file is not found. It is because resources are in slightly different dir. To make it work, move the `ramain` directory from `_internal` one level up (so it is on the same level as `_internal`).

## Ubuntu
  1. Run `sudo apt-get install python3.10-tk`,
  2. run `pip install -r requirements.txt`,
  3. run `python main.py`

## Conda
  1. `conda env create -f environment.yml`

