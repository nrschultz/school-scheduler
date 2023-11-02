from pulp import *

prob = LpProblem("BreweryProblem", LpMinimize)

wbDict = {}
for warehouse in ["A", "B"]:
    wbDict[warehouse] = {}
    for bar in range(1, 6):
        wbDict[warehouse][bar] = LpVariable("wh"+warehouse+" bar"+str(bar),0, None, LpInteger)

prob +=  (
    wbDict["A"][1] * 2 
    + wbDict["A"][2] * 4
    + wbDict["A"][3] * 5
    + wbDict["A"][4] * 2
    + wbDict["A"][5] * 1
    + wbDict["B"][2] * 3
    + wbDict["B"][1] * 1 
    + wbDict["B"][3] * 3
    + wbDict["B"][4] * 2
    + wbDict["B"][5] * 3
)

for (warehouse, supply) in [("A", 1000), ("B", 4000)]:
    prob += (
        wbDict[warehouse][1]
        + wbDict[warehouse][2] 
        + wbDict[warehouse][3] 
        + wbDict[warehouse][4] 
        + wbDict[warehouse][5]
        <= supply
    )

for (bar, request) in [(1, 500), (2, 900), (3, 1800), (4, 200), (5, 700)]:
    prob += wbDict['A'][bar] + wbDict['B'][bar] >= request
    prob += wbDict['A'][bar] >= 0
    prob += wbDict['B'][bar] >= 0




# The problem data is written to an .lp file
prob.writeLP("BreweryProblem.lp")

# The problem is solved using PuLP's choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
for v in prob.variables():
    print(v.name, "=", v.varValue)

# The optimised objective function value is printed to the screen
print("Total Cost of shipping = ", value(prob.objective))