# Group Builder

A simpl GUI application to create groups of people given a CSV file or the number of people per group with the number of groups that should be created.
It was build using WxPython in the context of an educational.

### Installation
Note: Python version `>=3.12.0` required.

1. Create venv: `python3 -m venv venv`
2. Activate venv (on linux: `bash venv/bin/activate`)
3. Install dependencies: `pip -r requirements.txt`
4. Run `python main.py`

### Dev Notes:
- In projects root `pyreverse -o png -p GroupBuilder .` to regenerate UML.
- In `./docs` run  `sphinx-build -M html source/ build/` to regenerate documentation.
- Archlinux wxPython build dependencies: `gtk3 wxwidgets-gtk3 make gcc`
- To build wxPython on archlinux use `LD_LIBRARY_PATH='$(pkg-config --cflags gtk+-3.0)' pip install wxPython` (assuming all dependencies installed).