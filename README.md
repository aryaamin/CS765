# CS765

## Required Libraries

The following libraries are required to run the code:

- **numpy**: A library for numerical computing with Python.
- **argparse**: A library for parsing command-line arguments.

## Installation Instructions

You can install these libraries using pip, the Python package manager.

```
pip install numpy argparse
```

## Usage

```bash
usage: python main.py [-h] [-n NUM_NODES] [--z0 Z0] [--z1 Z1] [--ttx TTX] [--I I]

options:
  -h, --help            show this help message and exit
  -n NUM_NODES, --num_nodes NUM_NODES
                        number of nodes in the network
  --z0 Z0               fraction of slow nodes in the network
  --z1 Z1               fraction of nodes with low CPU in the network
  --ttx TTX             mean generation time
  --I I                 inter arrival time
```

## Outputs

- `output/blockchain` contains the generated tree files
- `output/logs` contains the log files

