from polytabloid import find_solution
from partition import partition_gen, Partition
from argparse import ArgumentParser
import sqlite3
import sys

def print_query(query, families=False, pad=1):
    if type(query) in (sqlite3.Cursor, list):
        longest = ""
        results = []
        for q in query:
            results.append(q)
            longest = max((q[1], longest), key=len) # to ensure proper padding
        for r in results:
            print_query(r, families=families, pad=len(longest))
        return
    n, p_str, sol = query
    family = ""
    if families:
        _p = Partition(*map(int, p_str.split(",")))
        if _p.is_one_dimensional():
            family = "[1D]"
        if _p.is_hook():
            family = "[HOOK]"
        elif _p.is_self_conjugate():
            family = "[SELF-CONJ]"
    print u"{:{pad}} \u22a2 {:2}: solution {} {}".format("(" + p_str + ")", n, sol, family, pad=pad+2).encode("utf-8") 

if __name__ == "__main__":
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    # Initial database setup
    cur.execute("CREATE TABLE IF NOT EXISTS specht (n integer, partition text primary key, solution integer)")
    conn.commit()

    parser = ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Print additional status info while running.")
    parser.add_argument("--regen", help="Begin automation, overwriting previous database contents.", action="store_true")
    parser.add_argument("-p", help="Query by partition.", nargs="+")
    parser.add_argument("-n", help="Query by number being partitioned.", type=int)
    parser.add_argument("-s", help="Query by solution value.", type=int)
    parser.add_argument("-f", help="Query by partition family.", type=str)
    parser.add_argument("-a", action="store_true", help="Output entire data set.")
    parser.add_argument("-sf", action="store_true", help="Include partition family in output")
    args = parser.parse_args()

    if args.a:
        query = cur.execute("SELECT * FROM specht")
        print_query(query, families=args.sf)
        sys.exit(0)

    elif args.p:
        p_str = ",".join(args.p)
        query = cur.execute("SELECT * FROM specht WHERE partition=?", (p_str,)).fetchone()
        if query == None:
            print "No data found for ({}). Either the partition/conjugate is not 2-special or it is greater than the current maximum.".format(p_str)
        else:
            print_query(query, families=args.sf)
        sys.exit(0)


    elif args.f:
        if args.s:
            query = cur.execute("SELECT * FROM specht WHERE solution=?", (args.s,))
        elif args.n:
            query = cur.execute("SELECT * FROM specht WHERE n=?", (args.n,))
        else:
            query = cur.execute("SELECT * FROM specht")
        if args.f.lower() in ("hook", "hooks"):
            _match = (lambda p: p.is_hook())
        elif args.f.lower() in ("1d", "one dimensional", "one-dimensional"):
            _match = (lambda p: p.is_one_dimensional())
        elif args.f.lower() in ("self", "self-conj", "self-conjugate"):
            _match = (lambda p: p.is_self_conjugate())
        elif args.f.lower() == "none":
            _match = (lambda p: not p.is_self_conjugate() and not p.is_one_dimensional() and not p.is_hook())
        else:
            print "Family not recognized. Please use 'hook', '1d', 'self-conj', or 'none'."
            sys.exit(1)
        match = [(n, p_str, sol) for n, p_str, sol in query if _match(Partition(p_str))]
        print_query(match, families=args.sf)
        sys.exit(0)

    elif args.s:
        query = cur.execute("SELECT * FROM specht WHERE solution=?", (args.s,))
        print_query(query, families=args.sf)
        sys.exit(0)

    elif args.n:
        query = cur.execute("SELECT * FROM specht WHERE n=?", (args.n,))
        print_query(query, families=args.sf)
        max_n = cur.execute("SELECT max(n) FROM specht").fetchone()[0]
        if args.n >= max_n:
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
            p2 = p.conjugate()
            if p.is_2special() and p2.is_2special():
                p_str = ",".join(map(str, p.vals))
                p2_str = ",".join(map(str, p2.vals))
                # see if candidate or conjugate is already in db; otherwise compute & insert solution.
                in_db = cur.execute("SELECT * FROM specht WHERE partition=?", (p_str,)).fetchone()
                if in_db != None and not args.regen: # with --regen, override existing db contents
                    continue
                if p.num_row_perms() > p2.num_row_perms():
                    faster_p = p
                else:
                    faster_p = p2
                solution = find_solution(faster_p, verbose=args.verbose)
                # conjugate has same solution, so insert both
                cur.execute("INSERT OR REPLACE INTO specht VALUES (?,?,?),(?,?,?)", (n, p_str, solution % 2, n, p2_str, solution % 2))
                if args.verbose:
                    print "Inserting ({}, {}, {})".format(n, p_str, solution % 2)
                    print "Inserting ({}, {}, {})".format(n, p2_str, solution % 2)
                conn.commit()
        n += 1
