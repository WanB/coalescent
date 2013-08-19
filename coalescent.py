from numpy.random import rand, randint, exponential
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
  try:
    return T.root

  except AttributeError:
    for n in T.nodes():
      if T.out_degree(n) == 0:
        T.root = n
        return T.root

  return None


def is_same_edge(e1, e2):
  if (e1[0] == e2[0]) and (e1[1] == e2[1]):
    return True

  else:
    return False

def get_length(T, e):
  return T.get_edge_data(e[0], e[1])['length']

def get_lower_node(e):
  return e[0]

def get_upper_node(e):
  return e[1]

def get_lower_edges(T, e):
  if len(e) == 2:
    lower = get_lower_node(e)

  else:
    lower = e

  return T.in_edges(lower)

def get_other(T, e):
  upper = get_upper_node(e)
  level = get_lower_edges(T, upper)

  assert len(level)==2
  if is_same_edge(level[0], e):
    return level[1]

  else:
    assert is_same_edge(level[1], e)
    return level[0]

def get_upper_edges(T, e):
  if len(e) == 2:
    upper = get_upper_node(e)

  else:
    upper = e

  edges = T.out_edges(upper)
  if len(edges) == 1:
    return edges[0]

  elif len(edges) == 0:
    return None

  else:
    assert False

def is_top_edge(T, e):
  if get_upper_node(e) == get_root(T):
    return True

  else:
    return False

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
  result = []
  for i in range(n):
    d = len(cards)
    j = randint(0, d)
    result.append(cards[j])
    del cards[j]

  return result

def new_node(k):
  return crypt(str(k), 'aa')[2:]

def sample(n):
  T = DiGraph()
  alive = dict()
  heights = list()
  total = 0.0
  for i in range(n):
    alive[i] = 0.0

  k = n
  while k > 1:
    event = exponential(1.0/binom(k, 2))
    total += event
    heights.append(total)
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
  T.heights = heights

  return T

def verify(T):
  for node in T.nodes():
    i = len(T.in_edges(node))
    assert i == 0 or i == 2

    j = len(T.out_edges(node))
    assert j == 1 or j == 0

  return True
