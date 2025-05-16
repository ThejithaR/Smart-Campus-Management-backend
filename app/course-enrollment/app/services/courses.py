from app.supabase.supabaseClient import supabase
from app.services.lecturers import assign_course_to_lecturer
from app.models.course_models import AddCourseRequestModel

async def get_enrolled_courses(data: dict):
    reg_number = data.get("reg_number")
    try:
        response = (
            supabase
            .from_("Enrollments")
            .select("Courses(*)")
            .eq("reg_number", reg_number)
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error fetching enrolled courses: {response.status_code} - {response.error}")

        # Flatten "Courses" into top-level dicts
        enrolled_courses = [row["Courses"] for row in response.data if "Courses" in row]

        print(f"✅ Enrolled Courses: {enrolled_courses}")
        return enrolled_courses

    except Exception as e:
        raise Exception(f"An error occurred while fetching enrolled courses: {str(e)}")
    
async def get_eligible_courses(data: dict):
    reg_number = data.get("reg_number")
    try:
        # Step 1: Get student's semester
        student_response = (
            supabase
            .from_("Student profiles")
            .select("semester")
            .eq("reg_number", reg_number)
            .single()
            .execute()
        )

        # if student_response:
        #     raise Exception(f"Failed to fetch semester: {student_response.error}")

        semester = student_response.data["semester"]
        print(f"🎓 Student Semester: {semester}")

        # Step 2: Get eligible courses for that semester
        courses_response = (
            supabase
            .from_("Courses")
            .select("*")
            .eq("semester", semester)
            .execute()
        )

        # if courses_response:
        #     raise Exception(f"Failed to fetch courses: {courses_response.error}")

        print(f"✅ Eligible Courses: {courses_response.data}")
        return courses_response.data
    

    except Exception as e:
        raise Exception(f"An error occurred while fetching eligible courses: {str(e)}")
    
async def get_eligible_courses_yet_to_enroll(data: dict):
    reg_number = data.get("reg_number")
    try:
        # Step 1: Get student's semester
        student_response = (
            supabase
            .from_("Student profiles")
            .select("semester", "year")
            .eq("reg_number", reg_number)
            .single()
            .execute()
        )

        # if student_response:
        #     raise Exception(f"Failed to fetch semester: {student_response.error}")

        semester = student_response.data["semester"]
        year = student_response.data["year"]
        print(f"🎓 Student Year: {year} Semester: {semester}")

        # Step 2: Get eligible courses for that semester and year
        courses_response = (
            supabase
            .from_("Courses")
            .select("*")
            .eq("year", year)
            .eq("semester", semester)
            .execute()
        )

        # if courses_response:
        #     raise Exception(f"Failed to fetch courses: {courses_response.error}")

        eligible_courses = courses_response.data

        # Step 3: Get already enrolled courses
        enrolled_courses_response = (
            supabase
            .from_("Enrollments")
            .select("Courses(*)")
            .eq("reg_number", reg_number)
            .execute()
        )

        # if enrolled_courses_response:
        #     raise Exception(f"Failed to fetch enrolled courses: {enrolled_courses_response.error}")

        enrolled_courses = [row["Courses"] for row in enrolled_courses_response.data if "Courses" in row]

        # Step 4: Filter out already enrolled courses from eligible courses
        eligible_courses_yet_to_enroll = [
            course for course in eligible_courses if course not in enrolled_courses
        ]

        print(f"✅ Eligible Courses Yet to Enroll: {eligible_courses_yet_to_enroll}")
        return eligible_courses_yet_to_enroll

    except Exception as e:
        raise Exception(f"An error occurred while fetching eligible courses yet to enroll: {str(e)}")
    
async def get_assigned_courses(data: dict):
    reg_number = data.get("reg_number")
    try:
        response = (
            supabase
            .from_("Assigned")
            .select("Courses(*)")
            .eq("lecturer_reg_number", reg_number)
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error fetching assigned courses: {response.status_code} - {response.error}")

        # Flatten "Courses" into top-level dicts
        assigned_courses = [row["Courses"] for row in response.data if "Courses" in row]

        print(f"✅ Assigned Courses: {assigned_courses}")
        return assigned_courses

    except Exception as e:
        raise Exception(f"An error occurred while fetching assigned courses: {str(e)}")
    
async def get_all_courses():
    try:
        response = (
            supabase
            .from_("Courses")
            .select("*")
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error fetching all courses: {response.status_code} - {response.error}")

        print(f"✅ All Courses: {response.data}")
        return response.data
    except Exception as e: 
        raise Exception(f"An error occurred while fetching all courses: {str(e)}")
    
async def get_all_courses_yet_to_assign(data: dict):
    reg_number = data.get("reg_number")
    try:
        # Step 1: Get all courses
        all_courses_response = (
            supabase
            .from_("Courses")
            .select("*")
            .execute()
        )

        # if all_courses_response.error:
        #     raise Exception(f"Error fetching all courses: {all_courses_response.status_code} - {all_courses_response.error}")

        all_courses = all_courses_response.data

        # Step 2: Get already assigned courses
        assigned_courses_response = (
            supabase
            .from_("Assigned")
            .select("Courses(*)")
            .eq("lecturer_reg_number", reg_number)
            .execute()
        )

        # if assigned_courses_response.error:
        #     raise Exception(f"Error fetching assigned courses: {assigned_courses_response.status_code} - {assigned_courses_response.error}")

        assigned_courses = [row["Courses"] for row in assigned_courses_response.data if "Courses" in row]

        # Step 3: Filter out already assigned courses from all courses
        courses_yet_to_assign = [
            course for course in all_courses if course not in assigned_courses
        ]

        print(f"✅ Courses Yet to Assign: {courses_yet_to_assign}")
        return courses_yet_to_assign

    except Exception as e:
        raise Exception(f"An error occurred while fetching courses yet to assign: {str(e)}")
    
    
async def add_new_course(data: dict):
    # course_code = data.get("course_code")
    # course_name = data.get("course_name")
    # course_description = data.get("course_description")
    # year = data.get("year")
    # semester = data.get("semester")
    # day_of_the_week = data.get("day_of_the_week")
    # start_time = data.get("start_time")
    # lecturer_reg_numbers = data.get("lecturer_reg_numbers")

    add_new_course_request = AddCourseRequestModel(**data)
    course_code = add_new_course_request.course_code
    course_name = add_new_course_request.course_name
    course_description = add_new_course_request.course_description
    year = add_new_course_request.year
    semester = add_new_course_request.semester
    credits = add_new_course_request.credits
    day_of_week = add_new_course_request.day_of_week
    start_time = add_new_course_request.start_time
    lecturer_reg_numbers = add_new_course_request.lecturer_reg_numbers




    try:
        # Check if the course already exists
        existing_course = (
            supabase
            .from_("Courses")
            .select("*")
            .eq("course_code", course_code)
            .execute()
        )

        if existing_course.data:
            return {"message": "Course already exists."}

        print(f"Adding new course {course_code} - {course_name} for semester {semester}")
        # Add the new course
        response = (
            supabase
            .from_("Courses")
            .insert({
                "course_code": course_code, 
                "course_name": course_name, 
                "course_description": course_description,
                "year": year,
                "semester": semester,
                "credits": credits,
                "day_of_week": day_of_week,
                "start_time": start_time,
                })
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error adding new course: {response.status_code} - {response.error}")

        # Assign the course to the lecturer
        for lecturer_reg_number in lecturer_reg_numbers:
            print(f"Assigning course {course_code} to lecturer {lecturer_reg_number}")
            await assign_course_to_lecturer(course_code, lecturer_reg_number)

        return {"message": "Successfully added new course."}

    except Exception as e:
        raise Exception(f"An error occurred while adding new course: {str(e)}")