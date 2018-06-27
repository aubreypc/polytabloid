# Installation

Requires Python 2.7 and Pip / VirtualEnv.

Clone the repository and run 

```
pip install -r requirements.txt
```
# Usage

Running `python main.py` without arguments causes the script to begin automation mode. In this mode, the database is queried to find the largest integer *n* whose partitions are in the database. All partitions of *n* will then be generated, and the program will determine whether the Specht module associated with each partition has a one-dimensional summand, inserting this information into the database. With the `--regen` flag, the script will regenerate solution data for every integer *n* >= 2, and every partition of each *n*.

Once the database has been populated in automation mode, the command line interface allows for 2 types of querying. To search a specific partition's data, e.g. (3,1,1), run `python main.py -p 3 1 1`. To find this data for all partitions of 5 rather than just for (3,1,1), instead run `python main.py -n 5`.
