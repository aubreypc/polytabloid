from polytabloid import find_solution
from partition import partition_gen, Partition
from argparse import ArgumentParser
import sqlite3
import sys

if __name__ == "__main__":
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    parser = ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--regen", help="Begin automation, overwriting previous database contents", action="store_true")
    parser.add_argument("-qp", help="Query by partition.", nargs="+")
    parser.add_argument("-qn", help="Query by number being partitioned.", type=int)
    args = parser.parse_args()

    if args.qp:
        p_str = ",".join(args.qp)
        query = cur.execute("SELECT solution FROM specht WHERE partition=?", (p_str,)).fetchone()
        if query == None:
            print "No data found for ({}). Either the partition/conjugate is not 2-special or it is greater than the current maximum.".format(p_str)
        else:
            print "({}): sum congruent to {} (mod 2).".format(p_str, query[0])
        sys.exit(0)

    elif args.qn:
        query = cur.execute("SELECT * FROM specht WHERE n=?", (args.qn,))
        for _,p,sol in query:
            print "({}): sum congruent to {} (mod 2).".format(p, sol)
        max_n = cur.execute("SELECT max(n) FROM specht").fetchone()[0]
        if args.qn >= max_n:
            print "WARNING: given n is greater than or equal to maximum in database. Above list may be incomplete."
        sys.exit(0)
        

    # Automation mode:
    # find the the largest n currently in the database,
    # and figure out which partitions of n still need to be generated.
    n = cur.execute("SELECT max(n) FROM specht").fetchone()[0]
    if args.regen or not n:
        n = 2 
    while True:
        p_gen = partition_gen(n)
        for p in p_gen:
            p = Partition(*p)
            if p.is_2special() and p.conjugate().is_2special():
                print p.vals
                p_str = ",".join(map(str, p.vals))
                # see if candidate is already in db; otherwise compute & insert solution.
                in_db = cur.execute("SELECT * FROM specht WHERE partition=?", (p_str,)).fetchone()
                if in_db != None and not args.regen: # with --regen, override existing db contents
                    continue
                solution = find_solution(p, verbose=args.verbose)
                cur.execute("INSERT OR REPLACE INTO specht VALUES (?,?,?)", (n, p_str, solution % 2))
                if args.verbose:
                    print "Inserting ({}, {}, {})".format(n, p_str, solution % 2)
                conn.commit()
        n += 1
