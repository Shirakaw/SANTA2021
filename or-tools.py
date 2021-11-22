import functools
import itertools
import math

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


# Configure the problem
from pandas._libs.internals import defaultdict

from SA_for_VRP_based_on_CFRS import display

N_STRINGS = 3
LETTERS = [
    '🎅',  # father christmas
    '🤶',  # mother christmas
    '🦌',  # reindeer
    '🧝',  # elf
    '🎄',  # christmas tree
    '🎁',  # gift
    '🎀',  # ribbon
]
WILDCARD = '🌟'  # star
N = len(LETTERS)
DEPOT = itertools.repeat('0', N)  # a starting dummy node
INF = 999  # number to represent "infinite distance", could try sys.maxsize for hard constraint

# Configure stopping conditions for the search
N_SOLUTIONS = None
N_MINUTES = 60
def make_nodes():
    perms = list(itertools.permutations(LETTERS, N))
    all_ = perms[:math.factorial(N-2)]  # permutations beginning with 🎅🤶
    some = perms[math.factorial(N-2):]  # everything else
    return [DEPOT] + (all_ * N_STRINGS) + some


def create_data_model():
    data = {}
    data['locations'] = make_nodes()
    data['num_vehicles'] = N_STRINGS
    data['depot'] = 0
    return data


data = create_data_model()
manager = pywrapcp.RoutingIndexManager(
    len(data['locations']),
    data['num_vehicles'],
    data['depot'],
)
routing = pywrapcp.RoutingModel(manager)
def distance(p, q):
    if p == DEPOT or q == DEPOT: return 0
    for n in range(N+1):  # never choose maximum distance nodes (the N+1 case)
        if p[n:] == q[:N-n]:
            return n
    return INF  # max distance N becomes distance infinity


def distance_callback(from_index, to_index):
    # Convert from the internal representation to an actual permutation
    from_node = manager.IndexToNode(from_index)
    from_perm = data['locations'][from_node]
    to_node = manager.IndexToNode(to_index)
    to_perm = data['locations'][to_node]
    return distance(from_perm, to_perm)


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
# Define a Length dimension that records the lengths of each schedule
dimension_name = 'Length'
routing.AddDimension(
    transit_callback_index,
    0,  # slack is additional fixed cost at each node; not applicable here
    10**16, # max length per route; set to some large-enough number
    True,  # start with total length of 0
    dimension_name)
length_dimension = routing.GetDimensionOrDie(dimension_name)
length_dimension.SetGlobalSpanCostCoefficient(100) # total cost += 100 * (max_length - min_length)

# Set constraint that each vehicle must have all permutations beginning with 🎅🤶
n_all = math.factorial(N-2)
for vehicle in range(N_STRINGS):
    for node in range(n_all):
        routing.SetAllowedVehiclesForIndex(
            [vehicle],
            manager.NodeToIndex(1+vehicle*n_all+node),
        )
search_parameters = pywrapcp.DefaultRoutingSearchParameters()

search_parameters.first_solution_strategy = \
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

search_parameters.local_search_metaheuristic = \
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH

# Define stopping conditions
if N_SOLUTIONS is not None:
    search_parameters.solution_limit = N_SOLUTIONS
if N_MINUTES is not None:
    search_parameters.time_limit.seconds = N_MINUTES * 60

search_parameters.log_search = True
solution = routing.SolveWithParameters(search_parameters)

def get_routes(data, manager, routing, solution):
    routes = defaultdict(list)
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            idx_node = manager.IndexToNode(index)
            if idx_node != data['depot']:
                routes[vehicle_id].append(idx_node)
            index = solution.Value(routing.NextVar(index))
    return routes


def route_to_schedule(route, nodes):
    def overlap(a, b):
        return max(i for i in range(len(b)+1) if a.endswith(b[:i]))

    def squeeze(ws):
        return functools.reduce(lambda a, b: a + b[overlap(a, b):], ws)

    return squeeze(["".join(nodes[i]) for i in route])
def get_schedules(routes):
    words = [route_to_schedule(routes[vehicle_id], data['locations'])
             for vehicle_id in range(data['num_vehicles'])]
    return words
import pandas as pd


if solution:
    routes = get_routes(data, manager, routing, solution)
    words = get_schedules(routes)

    submission = pd.Series(words, name='schedule')
    submission.to_csv('submission.csv', index=False)

    display(submission)
    display(submission.apply(len).rename("Lengths"))
