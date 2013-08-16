from numpy.random import exponential
from numpy.random import rand
from random import shuffle
from scipy.special import binom
from crypt import crypt
from networkx import DiGraph

def get_leaves(T):
  result = set()
  for n in T.nodes():
    if T.in_degree(n) == 0:
      result.add(n)

  return result

def num_leaves(T):
  return len(get_leaves(T))

def get_root(T):
  for n in T.nodes():
    if T.out_degree(n) == 0:
      return n

  return None

def get_length(T, e):
  return T.get_edge_data(e[0], e[1])['length']

def crawl_up(T, e):
  upper = e[1]
  lower = e[0]

  down = T.in_edges(upper)
  sel = None

  if down[0][0] == lower:
    sel = down[1]
    assert down[1][0] != lower

  elif down[1][0] == lower:
    sel = down[0]
    assert down[0][0] != lower

  else:
    print e
    print T.in_edges(e[0])
    print T.out_edges(e[0])
    assert False

  assert sel != None

  up = T.out_edges(upper)
  if len(up) == 0:
    return [sel]

  else:
    assert len(up) == 1
    return [sel, up[0]]

def crawl_down(T, e):
  return T.in_edges(e[0])

def branch_length(T):
  total = 0.0
  for e in T.edges():
    total += get_length(T, e)

  return total

def collapse(T):
  leaves = get_leaves(T)
  below = dict()
  root = get_root(T)
  for node in T.nodes():
    below[node] = set()

  for this in leaves:
    above = this
    while above != root:
      below[above].add(this)
      above = T.neighbors(above)[0]

  below[root] = leaves
  return below

def random_edge(T):
  edges = T.edges()
  u = rand()*branch_length(T)
  cdf = 0
  for e in edges:
    cdf += get_length(T, e)
    if cdf > u:
      return e

  assert False

def subset(s, n):
  cards = list(s)
  shuffle(cards)
  return cards[0:n]

def new_node(k):
  return crypt(str(k), 'aa')[2:]

def sample(n):
  T = DiGraph()
  alive = dict()
  for i in range(n):
    alive[i] = 0.0

  k = n
  while k > 1:
    event = exponential(1.0/binom(k, 2))
    for c in alive.keys():
      alive[c] += event

    [a, b] = subset(alive.keys(), 2)
    c = new_node(k)
    alive[a]
    alive[b]
    T.add_edge(a, c, length = alive[a])
    T.add_edge(b, c, length = alive[b])

    del alive[a]
    del alive[b]
    alive[c] = 0.0

    k -= 1

  T.below = collapse(T)

  return T

def verify(T):
  for node in T.nodes():
    i = len(T.in_edges(node))
    assert i == 0 or i == 2

    j = len(T.out_edges(node))
    assert j == 1 or j == 0

  return True
