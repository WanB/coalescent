from networkx import draw
from pylab import show
from numpy.random import rand
from numpy import nan, sum, isnan, where, zeros
from sys import exit, stdout
import coalescent
reload(coalescent)

def observe(T, mutation, p):
  N = coalescent.num_leaves(T)

  data = zeros((N), dtype=int)
  for i in T.below[mutation[0]]:
    data[i] = 1

  train = zeros((N), dtype=int)+nan
  test = zeros((N), dtype=int)+nan

  for i in range(N):
    if (1-p) > rand():
      train[i] = data[i]

    else:
      test[i] = data[i]

  for i in range(N):
    if train[i] == 1:
      assert i in T.below[mutation[0]]

  return (test, train)

def admits(T, mutation, train):
  N = coalescent.num_leaves(T)
  ones_below = 0
  ones_above = 0
  zeros_below = 0
  zeros_above = 0
  for i in range(N): 
    if i in T.below[mutation[0]]:
      if train[i] == 0:
        zeros_below += 1

      elif train[i] == 1:
        ones_below += 1

    else:
      if train[i] == 0:
        zeros_above += 1

      elif train[i] == 1:
        ones_above += 1

  if ((zeros_below == 0) and (ones_above == 0)) or ((zeros_above == 0) and (ones_below == 0)):
    return True

  else:
    return False

def get_size(T, edges):
  size = 0.0
  for edge in edges:
    size += coalescent.get_length(T, edge)

  return size

def total_size(T):
  return get_size(T, T.edges())

def get_solutions_slow(T, train):
  solutions = set()
  for edge in T.edges():
    if admits(T, edge, train):
      solutions.add(edge)

  return solutions

def get_solutions_fast(T, mutation, train):
  dd = set()
  solutions = set()
  solutions.add(mutation)
  lower = coalescent.get_lower_edges(T, mutation)
  if len(lower)>0:
    [e1, e2] = lower
    if admits(T, e1, train):
      dd.add(e1)

    if admits(T, e2, train):
      dd.add(e2)

  other = coalescent.get_other(T, mutation)
  if admits(T, other, train):
    dd.add(other)

  upper = coalescent.get_upper_edges(T, mutation)
  while upper != None:
    if admits(T, upper, train):
      solutions.add(upper)
      other = coalescent.get_other(T, upper)
      if admits(T, other, train):
        dd.add(other)

    else:
      break

    upper = coalescent.get_upper_edges(T, upper)

  while len(dd)>0:
    print dd, len(dd)
    nd = set()
    for edge in dd:
      if admits(T, edge, train):
        solutions.add(edge)

        lower = coalescent.get_lower_edges(T, edge)
        if len(lower)>0:
          [e1, e2] = lower
          nd.add(e1)
          nd.add(e2)

    dd = nd

  return solutions
  

def get_solutions(T, mutation, train):
  assert coalescent.verify(T)
  assert admits(T, mutation, train)
  solutions = set([mutation])

  dd = coalescent.crawl_down(T, mutation)
  uu = coalescent.crawl_up(T, mutation)

  dd.append(uu[0])
  while len(uu) > 1 and admits(T, uu[1], train):
    solutions.add(uu[1])
    dd.append(uu[0])
    uu = coalescent.crawl_up(T, uu[1])

  if admits(T, uu[0], train):
    solutions.add(uu[0])
    dd.append(uu[0])

  while len(dd)>0:
    nd = list()
    for edge in dd:
      if admits(T, edge, train):
        solutions.add(edge)
        for down in coalescent.crawl_down(T, edge):
          nd.append(down)

      dd = nd

  return solutions

def impute(T, edge, train):
  N = coalescent.num_leaves(T)
  imputed = zeros((N), dtype=int)-nan
  for i in where(isnan(train))[0]:
    fix = 1
    found = False
    for j in T.below[edge[0]]:
      if not(isnan(train[j])):
        if found:
          assert train[j] == fix

        if train[j] == 0:
          fix = 0

        elif train[j] == 1:
          fix = 1

        else:
          assert False

        found = True

    if i in T.below[edge[0]]:
      imputed[i] = fix

    else:
      imputed[i] = 1-fix

  return imputed

def get_accuracy(test, imputed):
  numer = 0.0
  denom = sum(~isnan(test)) 
  for i in where(~isnan(test))[0]:
    if imputed[i] == test[i]:
      numer += 1.0

  return numer / denom

def estimate_accuracy(T, mutation, p):
  (test, train) = observe(T, mutation, p)
  solutions = get_solutions_slow(T, train)
  size = get_size(T, solutions)
  total = 0.0
  for edge in solutions:
    imputed = impute(T, edge, train)
    acc = get_accuracy(test, imputed)
    prop = coalescent.get_length(T, edge) / size
    total += acc * prop

  return total
