# run(data (students, teachers, courses, rooms), options (# periods, class size range, teacher load))


# Student {
#     id
#     requiredCourseIds <Course>
#     electiveCourseIds <Course> (ranked order)
# }

# Teacher {
#     id
#     coursesCanTeach <Course>
# }

# Course {
#     id
#     room <Room>
#     period <Period>
# }

# Room {
#     id
# }

# Period {
#     id
# }

# objective (outcome happiness?)
# optimize for students getting electives that are ranked higher
# optimize for smaller teacher load
# optimize for smaller class sizes

# constraints
# students and teachers can only be in a single course per period 
# students must have x courses on their schedule
# teachers should have no less than x courses and no more than y courses on their schedule
# Only one course can be taught in a room at a time (no more courses at a time than available rooms)
# teachers must teach courses they are qualified for
# students must be enrolled in all of their required courses
# students must only be put in classes that are part of their required or elective courses
# sections of the same course should have class sizes no more than x% different

# approach
# generate all student-course-period options and teacher-course-period options

from pulp import *
import random
import pprint

pp = pprint.PrettyPrinter(indent=2)

M = 1000000 #sufficiently large constant for big-m-constraint pattern

def generateStudent(id, grade):
    possibleElectives = ["Band", "Shop", f'Spanish{grade}', f'French{grade}', f'Art', "PhysEd"]
    return {
        "id": id,
        "requiredCourses": [f'Math{grade}', f'Science{grade}', f'English{grade}'],
        "electiveCourses": random.choices(possibleElectives, k=3)
    }


def generateTeacher(id, courses): 
    return {
        "id": id,
        "qualifiedCourses": random.choices(courses, k=3)
    }

def main():
    problemName = "SchoolScheduleProblem"
    prob = defineProblem(problemName)
    # Run the solver
    # The problem data is written to an .lp file
    prob.writeLP(f'{problemName}.lp')
    print("problem data written, solving")

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])

    print("processing schedule data")
    studentSchedules = {}
    teacherSchedules = {}
    sroomSchedules = {}
    rroomSchedules = {}

    # roomId{1:[]}
    for v in prob.variables():

            [variableType, period, course, room, id] = v.name.split("_") 

            if variableType == "studentEnrollment":
                if v.varValue == 1:
                    currentSchedule = studentSchedules.get(id, {})
                    currentSchedule[period] = {"room": room, "course": course}
                    studentSchedules[id] = currentSchedule

                    if not sroomSchedules.get(room):
                        sroomSchedules[room] = {}
                    if not sroomSchedules[room].get(period):
                        sroomSchedules[room][period] = []
                    if course not in sroomSchedules[room][period]:
                        sroomSchedules[room][period].append(course)

            # if variableType == "teacherAssignment":
                
            #     currentSchedule = teacherSchedules.get(id, {})
            #     currentSchedule[period] = {"room": room, "course": course}
            #     teacherSchedules[id] = currentSchedule

            if variableType == "roomAssignment":
                print(v)
                if v.varValue == 1:
                    if not rroomSchedules.get(room):
                        rroomSchedules[room] = {}
                    if not rroomSchedules[room].get(period):
                        rroomSchedules[room][period] = []
                    if course not in rroomSchedules[room][period]:
                        rroomSchedules[room][period].append(course)
    # print(studentSchedules)

    pp.pprint(sroomSchedules)
    pp.pprint(rroomSchedules)

    # print(teacherSchedules)

def courseStatusForStudent(student, course):
    if course in student['requiredCourses']:
        return "required"
    elif course in student['electiveCourses']:
        return "elective"
    else:
        return "no_enrollment"

def defineProblem(problemName):
    prob = LpProblem(problemName, LpMinimize)

    # decision variables
    # for each student, period, course, section combination, is the student in the period-course-section
    
    # PERIODS = range(1,8)
    # COURSES = [
    #     "English1", "English2", "English3", "English4",
    #     "Science1", "Science2", "Science3", "Science4", 
    #     "History1", "History2", "History3", "History4", 
    #     "Math1", "Math2", "Math3", "Math4",
    #     "Spanish1", "Spanish2", "Spanish3", "Spanish4",
    #     "French1", "French2", "French3", "French4",
    #     "Art", "Band", "Shop", "PhysEd", "Health",
    # ]
    # ROOMS = [
    #     101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    #     201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
    #     301, 302, 303, 304, 305, 306, 307, 308, 309, 310,
    #     401, 402, 403, 404, 405, 406, 407, 408, 409, 410,
    # ]
    # STUDENTS = [generateStudent(id, random.choice([1,2,3,4])) for id in range(1000)]
    # TEACHERS = [generateTeacher(id, COURSES) for id in range(40)]

    
    PERIODS = range(1,5)
    COURSES = [
        "English1",
        "Science1",
        "Math1",
        "Spanish1",
        "French1",
        "Art", "Band", "Shop", "PhysEd",
    ]
    ROOMS = [
        101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    ]
    STUDENTS = [generateStudent(id, 1) for id in range(30)]
    TEACHERS = [generateTeacher(id, COURSES) for id in range(15)]

    sids = list([s["id"] for s in STUDENTS])
    tids = list([t["id"] for t in TEACHERS])

    studentEnrollment = LpVariable.dicts("studentEnrollment", (PERIODS, COURSES, ROOMS, sids), cat="Binary")
    teacherAssignment = LpVariable.dicts("teacherAssignment", (PERIODS, COURSES, ROOMS, tids), cat="Binary")
    roomAssignment = LpVariable.dicts("roomAssignment", (PERIODS, COURSES, ROOMS), cat="Binary")

    print("Generated Variables")

    # Objective - minimize # of teacher assingments across all course-room-periods
    prob += lpSum([teacherAssignment[p][c][r][tid] for p in PERIODS for c in COURSES for r in ROOMS for tid in tids])


    # class size
    for p in PERIODS:
        for c in COURSES:
            for r in ROOMS:
                # less than class size max
                prob += lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) <= 25 
                # no more than one teacher
                prob += lpSum([teacherAssignment[p][c][r][tid] for tid in tids]) <= 1
                # must have teacher if students enrolled
                prob += lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) <= lpSum([teacherAssignment[p][c][r][tid] for tid in tids]) * M
                # must have students if teacher assigned
                prob += lpSum([teacherAssignment[p][c][r][tid] for tid in tids]) <= lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) * M

                # prob += lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) >= 15 
                # prob += lpSum([teacherAssignment[p][c][r][sid] for tid in tids]) == 1
    
    #students have 1 course-room per period
    for sid in sids:
        for p in PERIODS:
            prob += lpSum([studentEnrollment[p][c][r][sid] for c in COURSES for r in ROOMS]) == 1
    
    #students have 1 of any given course
    for sid in sids:
        for c in COURSES:
            # lookup if course in required, if it is, set = 1, if it is in elective, set <= 1, if in neither, set = 0
            status = courseStatusForStudent(STUDENTS[sid], c)
            if status == "required":
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in ROOMS for p in PERIODS ]) == 1
            elif status == "elective":
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in ROOMS for p in PERIODS ]) <= 1
            else:
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in ROOMS for p in PERIODS ]) == 0

    #teachers have at most 1 course-room per period
    for tid in tids:
        for p in PERIODS:
            prob += lpSum([teacherAssignment[p][c][r][tid] for c in COURSES for r in ROOMS]) <= 1


    # Rooms can only have one course per period
    for r in ROOMS:
        for p in PERIODS:
            prob += lpSum([roomAssignment[p][c][r] for c in COURSES]) <= 1

    return prob


# # students in a class should be less than the max class size
# # a class must have a teacher and students
# # all students must have # classes == # periods
# # all teachers musht have # classes <= # periods
# # teachers must teach classes they are qualified for
# # students must be in classes they require
# # students may be in classes they elect

# prob += 

# def studentHappiness(studentPeriodCourses, studentData): 
#     return lpSum()
#     for period in studentPeriodCourses:
        


# def happiness(student_courses, student_preferences, teacher_courses, teacher_load_option):


if __name__ == "__main__":
    main()