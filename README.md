# uPyCraft-Qt5

This is my modified version of [uPyCraft](https://github.com/DFRobot/uPyCraft) based on [PyQt5](https://sourceforge.net/projects/pyqt/files/PyQt5/). I started from the version by japei100 found on [uPyCraft_PyQt5](https://github.com/jiapei100/uPyCraft_PyQt5). Unfortunately this version gave me a lot of problems which I try to correct in my new version. I keep his README file intact, explaining the environment required to run the program This has not changed


## Attention! This is work in progress and the program is only partly working!

## Environment
* Ubuntu 18.04.1
* Python 3.6.5
* Qt 5.11.1
* PyQt5


## Pre-Install

### 1. python3

```bash
$ python --version
Python 3.6.5
$ pip --version
pip 18.0 from ~/.local/lib/python3.6/site-packages/pip (python 3.6)
$ pip3 --version
pip 18.0 from ~/.local/lib/python3.6/site-packages/pip (python 3.6)

$ pip3 install -U pyinstaller --user
$ pip3 install -U pyflakes --user
$ pip3 install -U pyserial --user
```

### 2. QT

Download the NEWEST **qt-opensource-linux-x64-5.11.1.run** from https://www.qt.io/download, and:
```bash
    $ sudo ./qt-opensource-linux-x64-5.11.1.run
```

### 3. SIP

Refer to https://riverbankcomputing.com/software/sip/download
```bash
    $ pip3 install -U sip --user
```
        
### 4. PyQt5
   
Refer to https://sourceforge.net/projects/pyqt/files/PyQt5/
```bash
   $ pip3 install -U pyqt5 --user
```

### 5. QScintilla2
   
Refer to https://pypi.org/project/QScintilla/
```bash
$ pip3 install -U QScintilla --user
```


## Install uPyCraft

```bash
$ pyinstaller -F uPyCraft.py
```


## Run uPyCraft

```bash
$ cd dist
$ ./uPyCraft
```

![uPyCraft GUI](https://raw.githubusercontent.com/LongerVision/Resource/master/uPyCraft/uPyCraft.jpg)


## Boards

### Supported

* [ESP8266](https://arduino-esp8266.readthedocs.io/en/latest/boards.html)
* [ESP32](https://www.espressif.com/en/products/hardware/development-boards)
* [PyBoard](http://micropython.org/)
* [TPYBoardV202](https://github.com/TPYBoard)
* [TPYBoardV102](http://tpyboard.com/)
* [micro:bit](https://microbit.org/)

### To Be Supported

* [OpenMV](https://openmv.io/)


