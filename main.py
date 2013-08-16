import coalescent
reload(coalescent)
import admission
reload(admission)
from random import seed

N = 10
p = 0.25
s = 1238
seed(s)
T = coalescent.sample(N)
mutation = coalescent.random_edge(T)
acc = admission.estimate_accuracy(T, mutation, p)
print acc
