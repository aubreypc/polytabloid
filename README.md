# Description

Polytabloid is a Python program written as part of a research project during the summer of 2018. Its purpose is to search for new examples of Specht modules which are decomposable a one-dimensional summand.

# Installation

Requires Python 2.7 and Pip / VirtualEnv. By default, Redis is used as the Celery message broker, so that must be installed in order for concurrency to work.

Clone the repository and run 

```
pip install -r requirements.txt
```
# Tests

To run tests via pytest, run:
```
py.test ./tests
```
Note that concurrency tests will fail unless Redis and the Celery worker are running.

# Usage

Running `python main.py` without arguments causes the script to begin automation mode. In this mode, the database is queried to find the largest integer *n* whose partitions are in the database. All partitions of *n* will then be generated, and the program will determine whether the Specht module associated with each partition has a one-dimensional summand, inserting this information into the database. With the `--regen` flag, the script will regenerate solution data for every integer *n* >= 2, and every partition of each *n*. 

To run automation with the concurrent algorithm, use the `-c` flag. Ensure that Redis and the Celery worker are properly configured and running.

Once the database has been populated in automation mode, the command line interface allows for several types of querying. To output the entire data set, use `-a`. To search a specific partition's data, e.g. (3,1,1), run `python main.py -p 3 1 1`. To find this data for all partitions of 5 rather than just for (3,1,1), instead run `python main.py -n 5`. To show data for a particular family, use the `-f` flag. For example, to query all hook partitions with *n* = 15, use `python main.py -f hook -n 15`.
