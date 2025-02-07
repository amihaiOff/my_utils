# my_utils
This repo contains some useful functions for data analysis and visualization.

## Installation
Add to zshrc a line adding the repo to python path:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/my_utils
```
This will make it available to all kernels started from the terminal.
To make it available to the jupyterlab on my remote ec2, I should add code to the `~/.juniper/jupyter_notebook_config.py`:
```python
import os
os.environ['PYTHONPATH'] = os.path.expanduser("~/my_utils") + ":" + os.environ.get('PYTHONPATH', '')
```
