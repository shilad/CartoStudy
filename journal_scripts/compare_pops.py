"""
INSERT OVERWRITE DIRECTORY '/user/shiladsen/pop' select page_title, year, day, sum(view_count) from pageview_hourly
where year = 2017 and PMOD(day, 5) = 0 and hour = 10 and project = 'en.wikipedia'
group by page_title, year, day
"""

import os
import traceback
from collections import defaultdict
from pandas import read_csv
import numpy as np

dir = '/Users/a558989/Downloads/pop'

files = [dir + '/' + f  for f in os.listdir(dir) ]

sums = defaultdict(int)
counts = defaultdict(int)

for i, f in enumerate(files):
    print('reading %s (%d of %d)' % (f, i, len(files)))
    try:
        df = read_csv(f,
                      names=['title', 'year', 'day', 'count'],
                      delimiter='\001',
                      dtype={'title': str, 'count': np.int32, 'day': np.int32, 'year': np.int32},
                      engine = 'c',
                      header = None,
                      na_filter = False,
                      low_memory=False,
                      error_bad_lines=False,
                      warn_bad_lines=True,
                      memory_map=True
                      )
        for row in df.itertuples(index=False):
            sums[row.title] += row.count
            counts[row.title] += 1
    except:
        print('parsing of %s failed:' % (f,))
        traceback.print_exc()


avgs = [(sums[k] / counts[k], k) for k in sums]
avgs.sort(reverse=True)

top = set(title for (n, title) in avgs[:10000])

for i, (n, title) in enumerate(avgs[:100]):
    print('%d. %s (%d)' % (i+1, title, n))


vals = defaultdict(list)

for i, f in enumerate(files):
    print('reading %s (%d of %d)' % (f, i, len(files)))
    try:
        df = read_csv(f,
                      names=['title', 'year', 'day', 'count'],
                      delimiter='\001',
                      dtype={'title': str, 'count': np.int32, 'day': np.int32, 'year': np.int32},
                      engine = 'c',
                      header = None,
                      na_filter = False,
                      low_memory=False,
                      error_bad_lines=False,
                      warn_bad_lines=True,
                      memory_map=True
                      )
        print(f, df.shape)
        for row in df.itertuples(index=False):
            if row.title in top:
                vals[row.title].append(row.count)
    except:
        print('parsing of %s failed:' % (f,))
        traceback.print_exc()


medians = [(sorted(v)[len(v)/2], k) for k, v in vals.iteritems()]
medians.sort(reverse=True)

for i, (n, title) in enumerate(medians[:100]):
    print('%d. %s (%d)' % (i+1, title, n))