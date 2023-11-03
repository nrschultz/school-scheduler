import pandas as pd


def processData(prob):
    print("processing schedule data")
    scheduleData = []
    for v in prob.variables():
        if v.varValue == 1:
            [variableType, period, course, room, id] = v.name.split("_")
            scheduleData.append({
                "dataType": variableType,
                "id": f'{"t" if variableType == "teacherAssignment" else "s"}{id}',
                "period": period,
                "course": course,
                "room": room
            })
    dfSchedule = pd.DataFrame(scheduleData)
    return dfSchedule

def printStudentSchedules(dfSchedule):
    dfStudents = dfSchedule.loc[(dfSchedule["dataType"] == "studentEnrollment")]
    dfStudents.sort_values(by=["id", "period"])
    schedules = {}
    for (index, row) in dfStudents.iterrows():
        if row["id"] not in schedules:
            schedules[row["id"]] = dfStudents.loc[dfStudents["id"] == row["id"]]
    for studentSchedule in schedules.items():
        print(studentSchedule)

def printTeacherSchedules(dfSchedule):
    dfTeachers = dfSchedule.loc[(dfSchedule["dataType"] == "teacherAssignment")]
    dfTeachers.sort_values(by=["id", "period"])
    schedules = {}
    for (index, row) in dfTeachers.iterrows():
        if row["id"] not in schedules:
            schedules[row["id"]] = dfTeachers.loc[dfTeachers["id"] == row["id"]]
    for teacherSchedule in schedules.items():
        print(teacherSchedule)

def generateRoomSchedules(dfSchedule):
    dfSchedule.sort_values(by=["room", "period"])
    schedules = {}
    for (index, row) in dfSchedule.iterrows():
        if row["room"] not in schedules:
            schedules[row["room"]] = dfSchedule.loc[dfSchedule["room"] == row["room"]]
    return schedules

def printRoomSchedules(dfSchedule):
    schedules = generateRoomSchedules(dfSchedule)
    for roomSchedule in schedules.items():
        print(roomSchedule)

def verifySchedule(inputData, dfSchedule):
    violations = []
    # each room should only have 1 course per period, if a course exists, it should have a teacher and students, no more that x
    for room in inputData["rooms"]:
        for period in inputData["periods"]:
            dfRoomPeriod = dfSchedule.loc[(dfSchedule["room"] == room) & (dfSchedule["period"] == period)]
            coursesForRoomPeriod = [roomPeriodItem["course"] for _idx, roomPeriodItem in dfRoomPeriod.iterrows()]
            if len(set(coursesForRoomPeriod)) > 1:
                violations.append(f'Violation: room {room} during period {period} has more than one course {coursesForRoomPeriod}')
            
            teachersForRoomPeriod = [roomPeriodItem["id"] for _idx, roomPeriodItem in dfRoomPeriod.iterrows() if roomPeriodItem['dataType'] == "teacherAssignment"] 
            studentsForRoomPeriod = [roomPeriodItem["id"] for _idx, roomPeriodItem in dfRoomPeriod.iterrows() if roomPeriodItem['dataType'] == "studentEnrollment"] 
            if len(studentsForRoomPeriod) < 1 and len(teachersForRoomPeriod) > 1:
                violations.append(f'Violation: room {room} during period {period} has no students enrolled')

            if len(studentsForRoomPeriod) > 15:
                violations.append(f'Violation: room {room} during period {period} has more students ({len(studentsForRoomPeriod)}) than the max class size')

            if len(teachersForRoomPeriod) != 1 and len(studentsForRoomPeriod) > 0:
                violations.append(f'Violation: room {room} during period {period} has no teacher assigned')

    # each teacher should have a maximum of 1 course per period, and the courses should match their qualified courses
    for teacher in inputData["teachers"]:
        dfTeacher = dfSchedule.loc[dfSchedule["id"] == f't{teacher["id"]}']
        coursesForTeacher = set([teacherItem["course"] for _idx, teacherItem in dfTeacher.iterrows()])
        for course in coursesForTeacher:
            if course not in teacher["qualifiedCourses"]:
                violations.append(f'Violation: teacher {teacher["id"]} assigned to course ({course}) outside of their qualifications ({teacher["qualifiedCourses"]})')

        for period in inputData["periods"]:
            dfTeacherPeriod = dfTeacher.loc[dfTeacher["period"] == period]
            coursesForTeacherPeriod = [teacherPeriodItem["course"] for _idx, teacherPeriodItem in dfTeacherPeriod.iterrows()]
            if len(set(coursesForTeacherPeriod)) > 1:
                violations.append(f'Violation: teacher {teacher["id"]} during period {period} has more than one course {coursesForTeacherPeriod}')

    


    # each student should have one course per period, and the courses should include all required courses, the other courses should be a subset of their electives
    for student in inputData["students"]:
        for period in inputData["periods"]:
            dfStudentPeriod = dfSchedule.loc[(dfSchedule["period"] == period) & (dfSchedule["id"] == f's{student["id"]}')]
            coursesForStudentPeriod = [studentPeriodItem["course"] for _idx, studentPeriodItem in dfStudentPeriod.iterrows()]
            if len(set(coursesForStudentPeriod)) > 1:
                violations.append(f'Violation: student {student["id"]} during period {period} has more than one course {coursesForStudentPeriod}')

        dfStudent = dfSchedule.loc[dfSchedule["id"] == f's{student["id"]}']
        coursesForStudent = set([studentItem["course"] for _idx, studentItem in dfStudent.iterrows()])
        for course in coursesForStudent:
             if course not in student["requiredCourses"] + student["electiveCourses"]:
                violations.append(f'Violation: student {student["id"]} enrolled in course ({course}) outside of their requested courses ({student["requiredCourses"] + student["electiveCourses"]})')

        for course in student["requiredCourses"]:
            if course not in coursesForStudent:
                violations.append(f'Violation: student {student["id"]} not enrolled in required course ({course})')

    return violations