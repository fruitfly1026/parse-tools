#!/usr/bin/env python3

import sys
import gzip
import argparse
from functools import reduce

##############################################################################
#
# CONSTANTS
#

# Where the hosted files will be found.
DB_URL = 'http://www-users.cs.umn.edu/~shaden/frostt_data'

VERSION_STR = '0.1'
##############################################################################


##############################################################################
#
# Argument parsing
#

#prog_desc = "Build an index file for a FROSTT dataset.\n"

parser = argparse.ArgumentParser()
parser.add_argument('tensor', help='sparse tensor, .tns[.gz]')
parser.add_argument('-o', '--output', help='output file', type=str)
parser.add_argument('-t', '--title', help='tensor title', type=str)
parser.add_argument('-c', '--cite', help='file with bibtex entry', type=str)
parser.add_argument('-n', '--nnz', help='number of non-zeros', default=0, type=int)
parser.add_argument('--order', help='number of tensor modes', default=0, type=int)
parser.add_argument('--desc', help='description file', type=str)
parser.add_argument('-d', '--dims', help='comma-separated list of dimensions',
    type=str)
parser.add_argument('--tag', help='add a tag', action='append')

env = parser.parse_args()
#print(env)

##############################################################################



##############################################################################
#
# File parsing
#

def open_file(fname):
  if fname.endswith('gz'):
    return gzip.open(fname, 'rb')
  else:
    return open(fname, 'r')

def get_nnz(fin):
  for line in fin:
    if type(line) == bytes:
      line = line.decode('utf-8')
    if line[0] == '#':
      continue
    yield line.strip().split()
##############################################################################



##############################################################################
#
# Tensor info
#

description = ''
if env.desc:
  with open(env.desc, 'r') as desc_file:
    description = desc_file.read()

citation = ''
if env.cite:
  with open(env.cite, 'r') as cite_file:
    citation = cite_file.read()

nonzeros = env.nnz
order = env.order
dims = []
if env.dims:
  dims = [int(x) for x in env.dims.split(',')]

tags = []
if env.tag:
  tags = env.tag
##############################################################################


# Parse data from tensor file if necessary
if (nonzeros == 0) or (order == 0) or dims == []:
  with open_file(env.tensor) as fin:
    for nnz_list in get_nnz(fin):
      order = len(nnz_list) - 1
      nonzeros += 1

      # store dims if necessary
      if not env.dims:
        if not dims:
          dims = [0] * order
        for m in range(order):
          dims[m] = max(dims[m], int(nnz_list[m]))

# determine output file
if env.output is None:
  env.output = env.tensor.replace('.tns', '.md')
  if env.tensor.endswith('.gz'):
    env.output = env.output[:-3]


# write markdown file
with open(env.output, 'w') as fout:
  print('---', file=fout)
  if env.title:
    print('title: {}\n'.format(env.title), file=fout)
  else:
    print('title: {}\n'.format(env.output.replace('.md', '')), file=fout)

  print('description: >\n  {}\n'.format(description), file=fout)

  print("order: '{}'".format(order), file=fout)
  print("nnz: '{:,d}'".format(nonzeros), file=fout)

  dim_str= ['{:,d}'.format(d) for d in dims]
  print('dims: {}'.format(dim_str[:order]), file=fout)
  
  density = float(nonzeros) / reduce(lambda x, y: float(x) * float(y), dims)
  print("density: '{:0.3e}'".format(density), file=fout)

  print('files:', file=fout)
  basename = env.tensor[env.tensor.rfind('/')+1 :]
  print(' - [Tensor, "{}/{}"]\n'.format(DB_URL, basename), file=fout)

  print('citation: >\n  {}\n'.format(citation), file=fout)
  print('tags: [{}]'.format(', '.join(tags)), file=fout)
  print('\n# generated by build_tensor v{}'.format(VERSION_STR), file=fout)
  print('---', file=fout)


