from pulp import *
import input_data  
import output
import model

def main():
    problemName = "SchoolScheduleProblem"

    data = input_data.generateInputData()

    prob = model.defineModel(problemName, data)
    # Run the solver
    # The problem data is written to an .lp file
    prob.writeLP(f'{problemName}.lp')
    print("problem data written, solving")

    # The problem is solved using PuLP's choice of Solver
    solver = PULP_CBC_CMD(timeLimit=60*5)
    prob.solve(solver)

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])
    if prob.status != 1:
        print("No solution")
        return

    df = output.processData(prob)
    # output.printStudentSchedules(df)
    # output.printTeacherSchedules(df)
    output.printRoomSchedules(df)
    


if __name__ == "__main__":
    main()