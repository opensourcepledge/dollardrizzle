#!/usr/bin/env python3
import csv
import os
import sys
from decimal import Decimal


# Helpers
# =======

def start_import_file(i):
    out = csv.writer(open(f'{org}-import-{i}.csv', 'w+'))
    out.writerow(['Maintainer username', 'Sponsorship amount in USD'])
    return out

def upcharge(target, fee):
    target = candidate = Decimal(target)
    perc_net = 1 - Decimal(fee) / 100
    one_cent = Decimal('0.01')
    while 1:
        if candidate * perc_net > target:
            return candidate
        candidate += one_cent


# Inputs
# ======

try:
    try:
        export_filepath = sys.argv[1]
    except IndexError:
        for filename in os.listdir('.'):
            if filename.startswith('github-explore-sponsors-for-'):
                export_filepath = filename
    export_filename = os.path.basename(os.path.realpath(export_filepath))
    org = export_filename[28:-15]
    if not org:
        raise heck
    print(f'Loading deps for {org} from {export_filepath} ...', file=sys.stderr)
except:
    print(f"Usage: {sys.argv[0]} [github-explore-sponsors-for-[your-org]-YYYY-MM-DD.csv]", file=sys.stderr)
    sys.exit()


# Load exclusions.
# ================

exclude = set()
try:
    # Originally written for a "CSV Report" from GitHub Enterprise:
    #   https://github.com/enterprises/[your-org]/people
    # Note that some of your employees use different logins for work and personal.
    # Good luck.
    exclusions_filename = f'{org}-exclusions.csv'
    exclusions_reader = csv.reader(open(exclusions_filename))
    headers = next(exclusions_reader)
    for row in exclusions_reader:
        rec = dict(zip(headers, row))
        roles = rec['GitHub com enterprise roles'].split(', ')
        if 'Member' in roles or 'Owner' in roles:
            exclude.add(rec['GitHub com login'])
except:
    print(f'Loading {exclusions_filename} ... not found.', file=sys.stderr)


# Load minimums.
# ==============

minimums = {}
try:
    minimums_filename = f'{org}-minimums.csv'
    for username, minimum in csv.reader(open(minimums_filename)):
        username = username[1:]
        minimum = minimum.split('$')[1]
        minimums[username] = minimum
except:
    print(f'Loading {minimums_filename} ... not found.', file=sys.stderr)


# Create import files.
# ====================

export_reader = csv.reader(open(export_filepath))
headers = next(export_reader)
to_sponsor = list()
ntotal = 0
for row in export_reader:
    username = row[0]
    ntotal += 1
    if username in exclude:
        print(f'  excluding {username}', file=sys.stderr)
        continue
    if username in minimums:
        print(f'  skipping  {username} (minimum {minimums[username]})', file=sys.stderr)
        continue
    to_sponsor.append(username)
nsponsored = len(to_sponsor)

i = j = 1
out = start_import_file(i)
for username in sorted(to_sponsor):
    if j > 100:
        j = 1
        i += 1
        out = start_import_file(i)
    out.writerow([username, 1])
    j += 1

monthly = nsponsored * 1
print(f'Writing {i} import file(s) ... done. Result:')
print(f'${monthly} / mo = ${monthly * 12} / yr | {nsponsored} / {ntotal} = {int(nsponsored / ntotal * 100)}%')
print(f'Invoice ${upcharge(monthly * 12, 3)} to cover 3% service fee.')
