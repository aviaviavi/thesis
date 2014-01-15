import random

#returns a partition of n, according to the chinese restaurant process.
#output is a list, each element 
def CRP(n):
    tables = []
    for i in range(n):
        next_table = which_table_crp(len(tables))
        if next_table != None:
            tables[next_table] += 1
        else:
            tables.append(1)
    return tables

#given a number of tables, and random number in (0,1), picks a table to sit at or None for a new table
def which_table_crp(n):
    if n == 0:
        return None
    rand = random.random()
    for i in range(n):
        thresh = (i + 1.0) / (n + 1.0)
        if rand < thresh:
            return i
    return None


class HawkesProcess():
    def __init__(self, base, n_p, n_q):
        self.base = base
        self.n_p = n_p
        self.n_q = n_q
        self.events = []

    def get_rate_at(self, t):
        return (self.base * self.n_p * self.n_q) + self.excitation(t)

    def excitation(self, t):
        return 0

    def simulate(self, t, maxtime=None, maxevents=None):
        pass
