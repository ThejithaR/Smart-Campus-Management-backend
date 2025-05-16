from app.supabase.supabaseClient import supabase

async def get_lecturers():
    try:
        # Fetch all lecturers from the "Lecturers" table
        response = (
            supabase
            .from_("faculty_member_profiles")
            .select("*")
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error fetching lecturers: {response.status_code} - {response.error}")

        print(f"✅ Lecturers: {response.data}")
        return response.data

    except Exception as e:
        raise Exception(f"An error occurred while fetching lecturers: {str(e)}")
    
async def assign_course_to_lecturer(course_code: str, lecturer_reg_number: str):
    try:
        # Check if the course exists
        course_response = (
            supabase
            .from_("Courses")
            .select("*")
            .eq("course_code", course_code)
            .execute()
        )

        if not course_response.data:
            return {"message": "Course does not exist."}

        # Assign the course to the lecturer
        response = (
            supabase
            .from_("Assigned")
            .insert({"course_code": course_code, "lecturer_reg_number": lecturer_reg_number})
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error assigning course: {response.status_code} - {response.error}")

        return {"message": "Course assigned successfully."}

    except Exception as e:
        raise Exception(f"An error occurred while assigning the course: {str(e)}")