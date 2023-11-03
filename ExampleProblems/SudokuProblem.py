from pulp import *

prob = LpProblem("SudokuProblem", LpMinimize) 

# objective
# zero un-populated squares?
# no objective????



# constraints
VALS = ROWS = COLS = range(1, 10)
boxes = [
    [(3 * i + k + 1, 3 * j + l + 1) for k in range(3) for l in range(3)]
    for i in range(3)
    for j in range(3)
]
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")

# value of each square should be 1-9 

for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1


for v in VALS:
    # each row should contain the numbers 1-9
    for r in ROWS:
        prob += lpSum([choices[v][r][c] for c in COLS]) == 1
    # each column should contain the numbers 1-9
    for c in COLS:
        prob += lpSum([choices[v][r][c] for r in ROWS]) == 1

    # each subgrid should contain the numbers 1-9
    for b in boxes:
        prob += lpSum([choices[v][r][c] for (r, c) in b]) == 1

# and value of starter squares should be set
# The starting numbers are entered as constraints
input_data = [
    (5, 1, 1),
    (6, 2, 1),
    (8, 4, 1),
    (4, 5, 1),
    (7, 6, 1),
    (3, 1, 2),
    (9, 3, 2),
    (6, 7, 2),
    (8, 3, 3),
    (1, 2, 4),
    (8, 5, 4),
    (4, 8, 4),
    (7, 1, 5),
    (9, 2, 5),
    (6, 4, 5),
    (2, 6, 5),
    (1, 8, 5),
    (8, 9, 5),
    (5, 2, 6),
    (3, 5, 6),
    (9, 8, 6),
    (2, 7, 7),
    (6, 3, 8),
    (8, 7, 8),
    (7, 9, 8),
    (3, 4, 9),
    (1, 5, 9),
    (6, 6, 9),
    (5, 8, 9),
]

for v, r, c in input_data:
    prob += choices[v][r][c] == 1

# Run the solver
# The problem data is written to an .lp file
prob.writeLP("SudokuProblem.lp")

# The problem is solved using PuLP's choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
solution = {}
for v in prob.variables():
    if v.varValue == 1:
        choiceData = v.name.split("_")
        if not solution.get(choiceData[2]): 
            solution[choiceData[2]] = {}
        solution[choiceData[2]][choiceData[3]] = choiceData[1]

solutionString = ""
for x in range(1,10):
    for y in range(1,10):
        solutionString += solution[str(x)][str(y)]
    solutionString += "\n"

print(solutionString)
    # print(v.name, "=", v.varValue)

