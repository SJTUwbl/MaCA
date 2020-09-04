# MaCA
![](https://img.shields.io/badge/language-python-green.svg)
![](https://img.shields.io/badge/platform-windows-green.svg)
![](https://img.shields.io/badge/platform-linux-green.svg)
![](https://img.shields.io/badge/platform-mac-green.svg)
![](https://img.shields.io/badge/stability-experimental-green.svg)

Multi-agent Combat Arena (MaCA) is a heterogeneous multi-agent distributed decision and control technology reasearch platform produced by CETC-TFAI team. It focuses on the application of AI technologies e.g. reinforcement learning in multi-agent cooperation and confrontation

![](https://leonfg.github.io/maca/resource/maca.gif)

## System Requirements
- Linux 64-bit or Mac OS with Python 3.6
- numpy 1.14.2 or later
- pygame 1.9.3 or later

There is no limitation on agents' structure. You can write rule-based algorithms or use deep learning frameworks.
## Quick Start Guide
### Installation
```bash
pip install -U numpy pandas pygame
git clone https://github.com/CETC-TFAI/MaCA.git
cd MaCA
export PYTHONPATH=$(pwd)/environment:$PYTHONPATH
```
### Run a combat between two agents
[fight_mp.py](fight_mp.py) can execute two agents. It uses two instances of a fixed-rule agent to fight each other by default.
```bash
python fight_mp.py
```
You can specify agents and map by input arguments. In addition an agent should provide a call interface follows the MaCa platform specification.
### Replay
MaCa can record runtime log while playing and training. Use [replay.py](replay.py) to perform a replay.

First, run [fight_mp.py](fight_mp.py) and enable log record function
```bash
python fight_mp.py --log
```

Then, run [replay.py](replay.py) to replay the log
```bash
python replay.py fix_rule_vs_fix_rule
```
The log structure of MaCA is a set of .macalog files, they will be saved in path "log/log-name/".
When you run the [replay.py](replay.py), You must input a "log-name" as the parameter to specify which log you want to replay.

For more information, see [tutorial](/doc/tutorial.md)