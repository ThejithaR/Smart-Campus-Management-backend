#from app.db import supabase
from app.supabase.supabaseConfig import supabase
from app.models.notification_model import courseNotificationAddRequest, oneRecipientNotificationAddRequest
import uuid
from datetime import datetime
from pydantic import ValidationError

async def add_course_notification(data: dict):

    try:
        notification_add_request = courseNotificationAddRequest(**data)
    except ValidationError as ve:
        print(ve.json())  # or ve.errors()
        return {"status": "error", "message": "Invalid input", "details": ve.errors()}

    sender_id = notification_add_request.sender_id
    course_code = notification_add_request.course_code
    title = notification_add_request.title
    message = notification_add_request.message


    # Validate input data
    # if not title or not message or not course_code or not sender_id:
    #     return {"status": "error", "message": "Missing required fields: title, message, course_code, or sender_id"}

    try:

        # validate course_code
        course_response = supabase.table("Courses").select("course_code").eq("course_code", course_code).execute()
        if not course_response.data:
            return {"status": "error", "message": f"Course {course_code} does not exist"}
        
        # validate sender_id
        faculty_response = supabase.table("faculty_member_profiles").select("reg_number").eq("reg_number", sender_id).execute()
        if not faculty_response.data:
            return {"status": "error", "message": f"Faculty member {sender_id} does not exist"}


        # Step 1: Get all students enrolled in the course
        enroll_response = supabase.table("Enrollments").select("reg_number").eq("course_code", course_code).execute()
        # if enroll_response.error:
        #     print(f"❌ Error fetching enrollments: {enroll_response.error}")
        #     return {"status": "error", "message": "Failed to fetch enrollments"}
        if not enroll_response.data:
            return {"status": "error", "message": f"No students enrolled in course {course_code}"}

        reg_numbers = [e['reg_number'] for e in enroll_response.data]

        # Step 2: Get UIDs of those students from Student profiles
        # student_response = supabase.table("Student profiles").select("UID, reg_number").in_("reg_number", reg_numbers).execute()
        # if student_response.error:
        #     print(f"❌ Error fetching student UIDs: {student_response.error}")
        #     return {"status": "error", "message": "Failed to fetch student profiles"}
        # if not student_response.data:
        #     return {"status": "error", "message": "No matching student profiles found"}



        # students = student_response.data

        # Step 3: Create notifications for each student
        notifications = []
        for reg_number in reg_numbers:
            notif = {
                "notification_id": str(uuid.uuid4()),
                "recipient_id": reg_number,
                "sender_id": sender_id,
                "course_code": course_code,
                "title": title,
                "message": message,
                "created_at": datetime.now().isoformat()
            }
            notifications.append(notif)

        # Step 4: Batch insert notifications
        response = supabase.table("Notifications").insert(notifications).execute()
        # if response.error:
        #     print(f"❌ Error inserting notifications: {response.error}")
        #     return {"status": "error", "message": "Failed to send notifications"}
        print(f"Response: {response}")

        print(f"✅ Sent notifications to {len(notifications)} students in course {course_code}")
        return {"status": "success", "count": len(notifications)}

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return {"status": "error", "message": str(e)}
    

async def add_one_recipient_notification(data: dict):
    try:
        notification_add_request = oneRecipientNotificationAddRequest(**data)
    except ValidationError as ve:
        print(ve.json())
        return {"status": "error", "message": "Invalid input", "details": ve.errors()}
    # Extract data from the request
    course_code = notification_add_request.course_code
    recipient_id = notification_add_request.recipient_id
    sender_id = notification_add_request.sender_id
    title = notification_add_request.title
    message = notification_add_request.message

    # Validate input data

    try:
        # validate course_code
        course_response = supabase.table("Courses").select("course_code").eq("course_code", course_code).execute()
        if not course_response.data:
            return {"status": "error", "message": f"Course {course_code} does not exist"}
        
        # validate sender_id
        faculty_response = supabase.table("faculty_member_profiles").select("reg_number").eq("reg_number", sender_id).execute()
        if not faculty_response.data:
            return {"status": "error", "message": f"Faculty member {sender_id} does not exist"}

        # validate recipient_id
        student_response = supabase.table("Student profiles").select("reg_number").eq("reg_number", recipient_id).execute()
        if not student_response.data:
            return {"status": "error", "message": f"Student with registration number {recipient_id} does not exist"}

        # Step 1: Create the notification
        notification = {
            "notification_id": str(uuid.uuid4()),
            "recipient_id": recipient_id,
            "sender_id": sender_id,
            "course_code": course_code,
            "title": title,
            "message": message,
            "created_at": datetime.now().isoformat()
        }

        # Step 2: Insert the notification into the database
        response = supabase.table("Notifications").insert(notification).execute()
        # if response.error:
        #     print(f"❌ Error inserting notification: {response.error}")
        #     return {"status": "error", "message": "Failed to send notification"}
        print(f"Response: {response}")

        print(f"✅ Sent notification to student {recipient_id} in course {course_code}")
        return {"status": "success", "notification_id": notification["notification_id"]}
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return {"status": "error", "message": str(e)}
