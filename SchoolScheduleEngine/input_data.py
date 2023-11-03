import random

def generateStudent(id, courses):
    return {
        "id": id,
        "requiredCourses": courses["required"],
        "electiveCourses": random.choices(courses["electives"], k=3)
    }

def generateTeacher(id, courses): 
    return {
        "id": id,
        "qualifiedCourses": random.choices(courses["electives"] + courses["required"], k=5)
    }

def generateInputData(options={}):
    periods = range(1, options.get("num_periods", 4) + 1)
    courses = {
        "electives": options.get("electiveCourses", ["Spanish1", "French1", "Art", "Band", "Shop", "PhysEd"]),
        "required": options.get("requiredCourses", ["English1", "Science1", "Math1", "History1"])
    }
    rooms = options.get("rooms", [
        "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "Gym", "BandRoom", "ShopRoom"
    ])
    room_course_pairs = options.get("room_course_pairs", [["Gym", "PhysEd"], ["BandRoom", "Band"], ["ShopRoom", "Shop"]])
    students = options.get("students", [generateStudent(id, courses) for id in range(options.get("num_students", 30))])
    teachers = options.get("teachers", [generateTeacher(id, courses) for id in range(options.get("num_teachers", 15))])    
    

    return {
        "periods": periods,
        "courses": courses,
        "rooms": rooms,
        "room_course_pairs": room_course_pairs,
        "students": students,
        "teachers": teachers
    }
    
