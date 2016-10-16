#!/usr/bin/env python

"""
Do group assignment avoiding minorities.

Author: Carl Sandrock
"""


import argparse
import pandas
import math

parser = argparse.ArgumentParser('Make groups which avoid minorities in minority')
parser.add_argument('filename', type=str)
parser.add_argument('size', type=int, help='Group size')

args = parser.parse_args()

readmethods = pandas.read_csv, pandas.read_excel

for reader in readmethods:
    print("Trying {}".format(reader))
    try:
        df = reader(args.filename, index_col='Nr')
        break
    except Exception as e:
        print('failed', e)
        continue
else:
    raise ValueError

Nstudents = len(df)

Ngroups = math.ceil(Nstudents/args.size)

print("{} students, {} groups".format(Nstudents, Ngroups))

import pulp

p = pulp.LpProblem('Groupassignment')

students = df.index.tolist()
minprops = df.columns.tolist()
groups = list(range(1, Ngroups+1))

# We reason by analogy to the set partitioning problem
# https://pythonhosted.org/PuLP/CaseStudies/a_set_partitioning_problem.html

possible_groups = [(s, g) for s in students for g in groups]
assigned = pulp.LpVariable.dicts('assigned', possible_groups,
                                 cat=pulp.LpBinary)
groupcount = pulp.LpVariable.dicts('groupcount', groups, cat=pulp.LpContinuous)
minority_groups = [(m, g) for m in minprops for g in groups]
mincount = pulp.LpVariable.dicts('mincount',
                                 minority_groups,
                                 cat=pulp.LpContinuous)
hasminority = pulp.LpVariable.dicts('hasminority',
                                    minority_groups,
                                    cat=pulp.LpBinary)

# Try to assign the larger groups first
p += sum([groupcount[g]*g for g in groups])
#p += sum([hasminority[mg] for mg in minority_groups])
M = args.size # This is big enough

for g in groups:
    # count students in groups
    p += (groupcount[g] == sum([assigned[(s, g)] for s in students]))
    # Limit group size
    p += (groupcount[g] <= args.size)
    p += (groupcount[g] >= args.size - 1)
    # Handle minorities
    for m in minprops:
        p += (mincount[(m, g)] == sum([assigned[(s, g)]*df.ix[s][m] for s in students]))
        p += (mincount[(m, g)] >= groupcount[g]*0.5 - M*(1 - hasminority[(m, g)]))
        p += (mincount[(m, g)] >= 0)
        p += (hasminority[(m, g)]*M >= mincount[(m, g)])

for s in students:
    # assign every student only once:
    p += (sum([assigned[(s, g)] for g in groups]) == 1)

p.solve()

assignedgroups = []
for s in students:
    for g in groups:
        if assigned[(s, g)].value() == 1:
            assignedgroups.append(g)

df['Group'] = assignedgroups
df.to_csv('output.csv')
