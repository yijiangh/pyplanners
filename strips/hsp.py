from collections import defaultdict, namedtuple
from heapq import heappush, heappop
from misc.numerical import INF

Pair = namedtuple('Node', ['cost', 'level'])

def compute_costs(state, goal, operators, op=max, unit=False):
    unprocessed = defaultdict(list) # TODO: store this in memory
    unsatisfied = {}
    for operator in operators + [goal]:
        unsatisfied[operator] = len(operator.conditions)
        for literal in operator.conditions:
            unprocessed[literal].append(operator)

    # ! Check here for the clamp precondition
    # compare with the initial state
    # precondition check
    # maybe put layering axioms or negated assumption

    literal_costs = {literal: Pair(0, 0) for literal in unprocessed if literal in state}
    operator_costs = {}
    queue = [(pair.cost, literal) for literal, pair in literal_costs.items()]

    def process_operator(operator):
        operator_cost = operator_level = 0
        if len(operator.conditions) != 0:
            operator_cost = op(literal_costs[literal].cost for literal in operator.conditions)
            operator_level = max(literal_costs[literal].level for literal in operator.conditions)
        operator_costs[operator] = Pair(operator_cost, operator_level)
        if operator == goal:
            # TODO: terminate earlier if the goal is achieved
            return True
        literal_cost = operator_cost + (operator.cost if not unit else 1)
        literal_level = operator_level + 1
        # literal_level = operator_level + (1 if not operator.is_axiom() else 0)
        for effect in operator.effects:
            # Only computes costs for relevant operators
            if (effect in unprocessed) and (effect not in literal_costs or
                                            (literal_cost < literal_costs[effect].cost)):
                literal_costs[effect] = Pair(literal_cost, literal_level)
                heappush(queue, (literal_cost, effect))
        return False

    for operator in unsatisfied:
        if unsatisfied[operator] == 0:
            process_operator(operator)
    while queue:
        _, literal = heappop(queue)
        if literal not in unprocessed:
            continue
        for operator in unprocessed[literal]:
            unsatisfied[operator] -= 1
            if unsatisfied[operator] == 0:
                process_operator(operator)
        del unprocessed[literal]

    return literal_costs, operator_costs

###########################################################################

def h_add(state, goal, operators):
    _, operator_costs = compute_costs(state, goal, operators, op=sum)
    return operator_costs[goal].cost if goal in operator_costs else INF

def h_max(state, goal, operators):
    _, operator_costs = compute_costs(state, goal, operators, op=max)
    return operator_costs[goal].cost if goal in operator_costs else INF

def h_add_unit(state, goal, operators):
    _, operator_costs = compute_costs(state, goal, operators, op=sum, unit=True)
    return operator_costs[goal].cost if goal in operator_costs else INF

def h_max_unit(state, goal, operators):
    _, operator_costs = compute_costs(state, goal, operators, op=max, unit=True)
    return operator_costs[goal].cost if goal in operator_costs else INF

###########################################################################

"""
def compute_costs(state, goal, operators, op=max, unit=False, greedy=True):
    costs = {}
    for literal in set(flatten(thing.conditions for thing in (operators + [goal]))):
        if literal in state:
            costs[literal] = 0

    unseen_operators = set(operators)
    queue = [(cost, literal) for literal, cost in costs.items()]
    heapify(queue)
    processed = set()
    while len(queue) != 0:
        _, literal = heappop(queue)
        if literal in processed: continue
        processed.add(literal)
        if greedy and all(literal in processed for literal in goal.conditions): return costs

        for operator in list(unseen_operators):
            if all(literal in processed for literal in operator.conditions):
                cost = op(costs[literal] for literal in operator.conditions) + (operator.cost if not unit else 1)
                for effect in operator.effects:
                    if effect not in costs or cost < costs[effect]:
                        costs[effect] = cost
                        heappush(queue, (cost, effect))
                unseen_operators.remove(operator)
    return costs
"""
