from app.supabase.supabaseClient import supabase
from app.rabbitmq.rabbitMQ_service import publish_message_with_reply
from app.config import COURSES_NOTIFICATIONS_QUEUE

async def enroll(data: dict):
    reg_number = data.get("reg_number")
    course_id = data.get("course_id")

    try:
        # Check if the student is already enrolled in the course
        existing_enrollment = (
            supabase
            .from_("Enrollments")
            .select("*")
            .eq("reg_number", reg_number)
            .eq("course_code", course_id)
            .execute()
        )

        if existing_enrollment.data:
            return {"message": "Already enrolled in this course."}

        print(f"Enrolling student {reg_number} in course {course_id}")
        # Enroll the student in the course
        response = (
            supabase
            .from_("Enrollments")
            .insert({"reg_number": reg_number, "course_code": course_id})
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error enrolling in course: {response.status_code} - {response.error}")

        # getting sender_id from faculty_member_profiles

        sender_id = (
            supabase
            .from_("Assigned")
            .select("reg_number")
            .eq("course_code", course_id)
            .execute()
        ).data[0]["reg_number"]

        # getting course name from courses
        course_name = (
            supabase
            .from_("Courses")
            .select("course_name")
            .eq("course_code", course_id)
            .single()
            .execute()
        ).data["course_name"]

        # Publish a message to the RabbitMQ queue for further processing
        response_from_notifications = await publish_message_with_reply(
            COURSES_NOTIFICATIONS_QUEUE,
            {
                "action": "addOneRecipientNotification",
                "payload": {
                    "course_id": course_id,
                    "recipient_id": reg_number,
                    "sender_id": sender_id,
                    "title": "New Course Enrollment",
                    "message": f"You have been successfully enrolled in the course {course_id} - {course_name}.",
                }
            }
        )

        print(f"Response from notifications service: {response_from_notifications}")

        return {"message": "Successfully enrolled in the course."}

    except Exception as e:
        raise Exception(f"An error occurred while enrolling in the course: {str(e)}")
    
async def unenroll(data: dict):
    reg_number = data.get("reg_number")
    course_id = data.get("course_id")

    try:
        # Check if the student is enrolled in the course
        existing_enrollment = (
            supabase
            .from_("Enrollments")
            .select("id")
            .eq("reg_number", reg_number)
            .eq("course_code", course_id)
            .execute()
        )

        if not existing_enrollment.data:
            return {"message": "Not enrolled in this course."}

        deleting_id = existing_enrollment.data[0]["id"]
        # Unenroll the student from the course
        response = (
            supabase
            .from_("Enrollments")
            .delete()
            .eq("id", deleting_id)
            .execute()
        )

        # if response.error:
        #     raise Exception(f"Error unenrolling from course: {response.status_code} - {response.error}")

        return {"message": "Successfully unenrolled from the course."}

    except Exception as e:
        raise Exception(f"An error occurred while unenrolling from the course: {str(e)}")