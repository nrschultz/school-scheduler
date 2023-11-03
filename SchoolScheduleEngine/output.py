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

def printRoomSchedules(dfSchedule):
    dfSchedule.sort_values(by=["room", "period"])
    schedules = {}
    for (index, row) in dfSchedule.iterrows():
        if row["room"] not in schedules:
            schedules[row["room"]] = dfSchedule.loc[dfSchedule["room"] == row["room"]]
    for roomSchedule in schedules.items():
        print(roomSchedule)