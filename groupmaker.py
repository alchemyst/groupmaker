#!/usr/bin/env python

"""
Do group assignment avoiding minorities.

Author: Carl Sandrock
"""


import math
import argparse
import pandas
import logging

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser('Make groups which avoid minorities in minority')
parser.add_argument('filename', type=str)
parser.add_argument('size', type=int, help='Group size')
parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=None,
                    help='Output filename (CSV)')
parser.add_argument('-i', '--idcol', type=str, default='Nr',
                    help='Name of column to use to identify students')
parser.add_argument('-m', '--markoverlap', type=float, default=0,
                    help='Amount to overlap marks')
parser.add_argument('-c', '--markgroupcount', type=int, default=0,
                    help='Minimum number of each mark group to assign to each group')

args = parser.parse_args()

readmethods = (('CSV', pandas.read_csv), ('Excel', pandas.read_excel))

for name, reader in readmethods:
    logging.info("Trying {}".format(name))
    try:
        df = reader(args.filename, index_col=args.idcol)
        break
    except Exception as e:
        print('failed', e)
        continue
else:
    raise ValueError

Nstudents = len(df)

Ngroups = math.ceil(Nstudents/args.size)

logging.info("{} students, {} groups".format(Nstudents, Ngroups))

import pulp

p = pulp.LpProblem('Groupassignment')

students = df.index.tolist()
minprops = [c for c in df.columns if c.endswith('nomin')]
groups = list(range(1, Ngroups+1))

markgroups = []
if "Grade" in df.columns:
    logging.info("Grade column detected, doing grade distribution")
    # TODO: Assign each student to a group
    cutpoints = pandas.np.linspace(0, 100, args.size+1)
    for markgroup, (lower, upper) in enumerate(zip(cutpoints, cutpoints[1:])):
        markgroupname = 'markgroup{}'.format(markgroup)
        markgroups.append(markgroupname)
        df[markgroupname] = df['Grade'].between(lower-args.markoverlap,
                                                upper+args.markoverlap)


# We reason by analogy to the set partitioning problem
# https://pythonhosted.org/PuLP/CaseStudies/a_set_partitioning_problem.html

possible_groups = [(s, g) for s in students for g in groups]
assigned = pulp.LpVariable.dicts('assigned',
                                 possible_groups,
                                 cat=pulp.LpBinary)
groupcount = pulp.LpVariable.dicts('groupcount',
                                   groups,
                                   cat=pulp.LpContinuous)
minority_groups = [(m, g) for m in minprops for g in groups]
mincount = pulp.LpVariable.dicts('mincount',
                                 minority_groups,
                                 cat=pulp.LpContinuous)
hasminority = pulp.LpVariable.dicts('hasminority',
                                    minority_groups,
                                    cat=pulp.LpBinary)
markgroupcombs = [(g, mg) for g in groups for mg in markgroups]
markgroupcount = pulp.LpVariable.dicts('markgroupcount',
                                       markgroupcombs,
                                       cat=pulp.LpContinuous)

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

    for mg in markgroups:
        # count students in mark groups
        p += (markgroupcount[g, mg] == sum([assigned[(s, g)]*df.ix[s][mg] for s in students]))
        p += (markgroupcount[g, mg] >= args.markgroupcount)


for s in students:
    # assign every student only once:
    p += (sum([assigned[(s, g)] for g in groups]) == 1)

statuscode = p.solve()
status = pulp.LpStatus[statuscode]

logging.info("Solution status: {}".format(status))

if status == "Infeasible":
    logging.error("Infeasible solution")
    raise ValueError("No feasible solution was found. Consider relaxing the constraints")

assignedgroups = []
for s in students:
    for g in groups:
        if assigned[(s, g)].value() == 1:
            assignedgroups.append(g)

df['Group'] = assignedgroups

if args.output:
    df.to_csv(args.output)
else:
    print(df)
