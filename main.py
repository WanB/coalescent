#!/usr/bin/env python
import argparse
import coalescent
reload(coalescent)
import admission
reload(admission)
from numpy.random import seed
from struct import unpack
from sys import stdout

with open('/dev/urandom', 'rb') as urandom:
  default_seed = unpack('i', urandom.read(4))

parser = argparse.ArgumentParser(description='Simulate the coalescent and estimate upper bound for imputation accuracy.')

parser.add_argument('--seed',
  dest='seed',
  type=int,
  default=default_seed,
  help='random seed used for the experiment.')

parser.add_argument('--N',
  dest='N',
  type=int,
  required=True,
  help='number of sequences to simulate')

parser.add_argument('--p',
  dest='p',
  type=float,
  required=True,
  help='proportion of entries to hold out (uniformly)')

args = parser.parse_args()
seed(args.seed)
N = args.N
p = args.p

stdout.write('acc total_size' )
for t in range(N-1):
  stdout.write(' h%d' % (t+1))

stdout.write('\n')
stdout.flush()

while True:
  T = coalescent.sample(N)
  mutation = coalescent.random_edge(T)
  acc = admission.estimate_accuracy(T, mutation, p)
  stdout.write('%f' % acc)
  stdout.write(' %f' % admission.total_size(T))
  for t in range(N-1):
    stdout.write(' %f' % T.heights[t])

  stdout.write('\n')
  stdout.flush()

