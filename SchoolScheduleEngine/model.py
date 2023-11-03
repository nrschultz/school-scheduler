from pulp import *


M = 1000000 #sufficiently large constant for big-m-constraint pattern
SMALL_M = .0001 #sufficiently small constant for small-m-constraint pattern


def defineModel(problemName, data):
    prob = LpProblem(problemName, LpMinimize)

    sids = [s["id"] for s in data["students"]]
    tids = [t["id"] for t in data["teachers"]]
    ALL_COURSES = data["courses"]["electives"] + data["courses"]["required"]

    studentEnrollment = LpVariable.dicts("studentEnrollment", (data["periods"], ALL_COURSES, data["rooms"], sids), cat="Binary")
    teacherAssignment = LpVariable.dicts("teacherAssignment", (data["periods"], ALL_COURSES, data["rooms"], tids), cat="Binary")
    # roomAssignment = LpVariable.dicts("roomAssignment", (data["periods"], data["courses"], data["rooms"]), cat="Binary")

    print("Generated Variables")

    # Objective - minimize # of teacher assingments across all course-room-periods
    # prob += lpSum([teacherAssignment[p][c][r][tid] for p in data["periods"] for c in data["courses"] for r in data["rooms"] for tid in tids])


    # class size
    for p in data["periods"]:
        for c in ALL_COURSES:
            for r in data["rooms"]:
                # less than class size max
                prob += lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) <= 15 
                # add a minimum class size (not working? or maybe the randomized data is hit or miss)
                # prob += 2 - lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) <= lpSum([studentEnrollment[p][c][r][sid] for sid in sids]) * SMALL_M

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
        for p in data["periods"]:
            prob += lpSum([studentEnrollment[p][c][r][sid] for c in ALL_COURSES for r in data["rooms"]]) == 1
    
    #students have 1 of any given course
    for sid in sids:
        for c in ALL_COURSES:
            # lookup if course in required, if it is, set = 1, if it is in elective, set <= 1, if in neither, set = 0
            status = courseStatusForStudent(data["students"][sid], c)
            if status == "required":
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in data["rooms"] for p in data["periods"] ]) == 1
            elif status == "elective":
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in data["rooms"] for p in data["periods"] ]) <= 1
            else:
                prob += lpSum([studentEnrollment[p][c][r][sid] for r in data["rooms"] for p in data["periods"] ]) == 0

    #teachers have at most 1 course-room per period
    for tid in tids:
        for p in data["periods"]:
            prob += lpSum([teacherAssignment[p][c][r][tid] for c in ALL_COURSES for r in data["rooms"]]) <= 1

    # rooms can only have one course-period
    for r in data["rooms"]:
        for p in data["periods"]:
            prob += lpSum([teacherAssignment[p][c][r][tid] for c in ALL_COURSES for tid in tids]) <= 1

    reserveRooms(prob, data, {"studentEnrollment": studentEnrollment, "teacherAssignment": teacherAssignment})

    # Future Idesa
    # one room per teacher or one teacher per room
    # one course per room
    # Subject to generalize course, a teacher will probably teach a subject but multiple courses
    # 

    return prob

def reserveRooms(prob, data, vars):
    for sid in [s["id"] for s in data["students"]]:
        for p in data["periods"]:
            for [room, course] in data["room_course_pairs"]:
                prob += lpSum([vars["studentEnrollment"][p][course][r][sid] for r in data["rooms"] if r != room]) == 0
                prob += lpSum([vars["studentEnrollment"][p][c][room][sid] for c in data["courses"]["electives"] + data["courses"]["required"] if c != course]) == 0


def courseStatusForStudent(student, course):
    if course in student['requiredCourses']:
        return "required"
    elif course in student['electiveCourses']:
        return "elective"
    else:
        return "no_enrollment"