# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import psycopg2
from datetime import datetime
import re
import uuid
from typing import Any, Text, Dict, List
import requests
from decouple import config

API_URL = config('API_BASE_URL')

def get_db_connection():
    return psycopg2.connect(
        host="db.fbpgrmhqzlobmtmpprvj.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="PpUxvZcvRe7yskSA"
    )
# -------------------------------
# ACTION 1: Submit Query Chat
# -------------------------------
class ActionSubmitQuery(Action):
    def name(self):
        return "action_submit_query"

    def run(self, dispatcher, tracker, domain):
        message = tracker.get_slot('query_message')
        user_reg_number = tracker.get_slot('user_reg_number')
        user_role = tracker.get_slot('user_role')  # "student" or "faculty"

        conn = get_db_connection()
        cursor = conn.cursor()

        if user_role == "student":
            cursor.execute(
                "INSERT INTO ChatQueries (query_text, student_reg_number) VALUES (%s, %s)",
                (message, user_reg_number)
            )
        elif user_role == "faculty":
            cursor.execute(
                "INSERT INTO ChatQueries (query_text, faculty_reg_number) VALUES (%s, %s)",
                (message, user_reg_number)
            )
        conn.commit()

        dispatcher.utter_message(text="Your query has been submitted successfully.")
        return []
# -------------------------------
# ACTION 1: Get Exam Schedule
# -------------------------------
class ActionGetExamSchedule(Action):
    def name(self):
        return "action_get_exam_schedule"

    def run(self, dispatcher, tracker, domain):
        # Retrieve metadata from the latest message
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)
            print("User reg number:", user_reg_number)
            print("User role:", user_role)

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []

        course_code = tracker.get_slot('course_code')
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT title, exam_date, start_time, location FROM "Exams" WHERE course_code = %s',
            (course_code,)
        )
        result = cursor.fetchone()

        if result:
            title, date, time, location = result
            dispatcher.utter_message(
                text=f"Exam '{title}' is on {date} at {time} in {location}."
            )
        else:
            dispatcher.utter_message(text="No exam found for that course.")

        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]

class ActionScheduleExam(Action):
    def name(self):
        return "action_schedule_exam"

    def run(self, dispatcher, tracker, domain):
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)
        else:
            user_reg_number = None
            user_role = None

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []

        if user_role != "faculty":
            dispatcher.utter_message(text="You are a student. You don't have access to schedule exams.")
            return []

        course_code = tracker.get_slot('course_code')
        title = tracker.get_slot('exam_title')
        date_str = tracker.get_slot('exam_date')
        start_time_str = tracker.get_slot('exam_start_time')
        end_time_str = tracker.get_slot('exam_end_time')
        start_time = tracker.get_slot('exam_start_time')
        end_time = tracker.get_slot('exam_end_time')
        location = tracker.get_slot('exam_location')
        print("User reg number:", user_reg_number)
        print("User role:", user_role)
        print("Course code:", course_code)
        print("Exam title:", title)
        print("Exam date:", date_str)
        print("Exam start time:", start_time_str)
        print("Exam end time:", end_time_str)
        print("Exam location:", location)
        if start_time:
            start_time = start_time.upper().replace("AM", "").replace("PM", "").strip()
        if end_time:
            end_time = end_time.upper().replace("AM", "").replace("PM", "").strip()

        if not all([course_code, title, date_str, start_time_str, end_time_str, location]):
            dispatcher.utter_message(
            text="Please provide complete exam details to schedule."
            )
            return []

        # Convert date and time strings to correct formats
        try:
            exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            dispatcher.utter_message(text="Please provide the date in YYYY-MM-DD and time in HH:MM format.")
            return []

        # 🟢 Step 1: Get Scheduled_by UID from API (instead of direct DB query)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get Scheduled_by UID using registration number
        cursor.execute(
            'SELECT "UID" FROM "faculty_member_profiles" WHERE reg_number = %s',
            (user_reg_number,)
        )
        result = cursor.fetchone()
        if not result:
            dispatcher.utter_message(text="No faculty member found with the provided registration number.")
            return []

        scheduled_by = result[0]  # UID

        # 🟢 Step 2: Prepare JSON data for POST
        payload = {
            "title": title,
            "start_time": start_time.strftime("%H:%M:%S"),  # Format time properly
            "end_time": end_time.strftime("%H:%M:%S"),  # Optional: You can collect from user later
            "course_code": course_code,
            "exam_date": exam_date.strftime("%Y-%m-%d"),
            "notified": False,
            "description": f"Exam for course {course_code}",  # Optional description
            "location": location,
            "scheduled_by": scheduled_by
        }
        print("Payload for scheduling exam:", payload)

        # 🟢 Step 3: Call the API to schedule exam
        try:
            response = requests.post(f"{API_URL}/api/exams/schedule", json=payload)

            if response.status_code == 200:
                dispatcher.utter_message(text=f"Exam '{title}' scheduled successfully.")
            else:
                dispatcher.utter_message(text=f"Failed to schedule exam. Server response: {response.text}")
        except Exception as e:
            dispatcher.utter_message(text=f"Error calling schedule API: {str(e)}")

        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]

# -------------------------------
# ACTION 2: Schedule Exam (Faculty only)
# -------------------------------
# class ActionScheduleExam(Action):
#     def name(self):
#         return "action_schedule_exam"

#     def run(self, dispatcher, tracker, domain):
#         # Retrieve metadata from the latest message
#         metadata = tracker.latest_message.get('metadata', None)

#         if metadata:
#             user_reg_number = metadata.get('user_reg_number', None)
#             user_role = metadata.get('user_role', None)

#         if not user_reg_number or not user_role:
#             dispatcher.utter_message(text="Unable to retrieve user information.")
#             return []

#         course_code = tracker.get_slot('course_code')
#         title = tracker.get_slot('exam_title')
#         date_str = tracker.get_slot('exam_date')
#         time_str = tracker.get_slot('exam_time')
#         if time_str:
#             time_str = time_str.upper().replace("AM", "").replace("PM", "").strip()
#         location = tracker.get_slot('exam_location')

#         if not all([course_code, title, date_str, time_str, location]):
#             dispatcher.utter_message(text="Please provide complete exam details to schedule.")
#             return []

#         if user_role != "faculty":
#             dispatcher.utter_message(text="You are a student. You don't have access to schedule exams.")
#             return []

#         print("User reg number:", user_reg_number)
#         print("User role:", user_role)
#         print("Course code:", course_code)
#         print("Exam title:", title)
#         print("Exam date:", date_str)
#         print("Exam time:", time_str)
#         print("Exam location:", location)
#         # Convert date and time strings to date/time objects
#         try:
#             exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#             start_time = datetime.strptime(time_str, '%H:%M').time()
#         except ValueError:
#             dispatcher.utter_message(text="Please provide the date in YYYY-MM-DD and time in HH:MM format.")
#             return []

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Get Scheduled_by UID using registration number
#         cursor.execute(
#             'SELECT "UID" FROM "faculty_member_profiles" WHERE reg_number = %s',
#             (user_reg_number,)
#         )
#         result = cursor.fetchone()
#         if not result:
#             dispatcher.utter_message(text="No faculty member found with the provided registration number.")
#             return []

#         scheduled_by = result[0]  # UID

#         # Generate UUID for exam_id
#         exam_id = str(uuid.uuid4())

#         # Now insert exam details
#         cursor.execute(
#             """
#             INSERT INTO "Exams" (Exam_id, Title, Course_code, Scheduled_by, Exam_date, Start_time, Location)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """,
#             (exam_id, title, course_code, scheduled_by, exam_date, start_time, location)
#         )
#         conn.commit()

#         dispatcher.utter_message(text=f"Exam '{title}' scheduled successfully by faculty member with reg no {user_reg_number}.")
#         return [
#             SlotSet("user_reg_number", user_reg_number),
#             SlotSet("user_role", user_role)
#         ]
class ActionGetProfile(Action):
    def name(self):
        return "action_get_profile"

    def run(self, dispatcher, tracker, domain):
        # Retrieve metadata from the latest message
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        if user_role == "student":
            cursor.execute(
                'SELECT * FROM "Student profiles" WHERE reg_number = %s',
                (user_reg_number,)
            )
            result = cursor.fetchone()
            profile_fields = ["id","reg_number","name", "faculty", "department", "year_of_study", "semester"]
        elif user_role == "faculty":
            cursor.execute(
                'SELECT * FROM "faculty_member_profiles" WHERE reg_number = %s',
                (user_reg_number,)
            )
            result = cursor.fetchone()
            profile_fields = ["id","reg_number","name", "designation", "faculty", "department"]
        else:
            dispatcher.utter_message(text="Unrecognized user role.")
            return []
        print("User reg number:", user_reg_number)
        print("User role:", user_role)
        print("Profile fields:", profile_fields)
        print("Profile result:", result)
        if result:
            profile_info = "\n".join(
                [f"{field}: {result[i]}" for i, field in enumerate(profile_fields)]
            )
            print("Profile info:", profile_info)
            dispatcher.utter_message(text=f"Your profile information:\n\n{profile_info}")
        else:
            dispatcher.utter_message(text="No profile found.")

        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]
# -------------------------------
# ACTION 3: Update Contact Info
# -------------------------------
class ActionUpdateProfile(Action):
    def name(self):
        return "action_update_profile"

    def run(self, dispatcher, tracker, domain):
        # Retrieve metadata from the latest message
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []


        attribute = tracker.get_slot('attribute')
        new_value = tracker.get_slot('new_value')

        print("attribute", attribute)
        print("new_value", new_value)

        if not attribute or not new_value:
            dispatcher.utter_message(text="Please provide the attribute and new value.")
            return []

        # Valid fields for each role
        student_fields = ["name", "faculty", "department", "year_of_study", "semester"]
        faculty_fields = ["name", "designation", "faculty", "department"]

        conn = get_db_connection()
        cursor = conn.cursor()

        print("attribute:", attribute)
        print("new_value:", new_value)

        if user_role == "student":
            if attribute not in student_fields:
                dispatcher.utter_message(text=f"Invalid attribute for students. You can update: {', '.join(student_fields)}.")
                return []
            query = f'UPDATE "Student profiles" SET "{attribute}" = %s WHERE reg_number = %s'
            cursor.execute(query, (new_value, user_reg_number))

        elif user_role == "faculty":
            if attribute not in faculty_fields:
                dispatcher.utter_message(text=f"Invalid attribute for faculty. You can update: {', '.join(faculty_fields)}.")
                return []
            query = f'UPDATE "faculty_member_profiles" SET "{attribute}" = %s WHERE reg_number = %s'
            cursor.execute(query, (new_value, user_reg_number))

        else:
            dispatcher.utter_message(text="Unrecognized user role.")
            return []

        conn.commit()
        dispatcher.utter_message(text=f"Your {attribute} has been updated to {new_value}.")
        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]

# -------------------------------
# ACTION 4: Check Attendance
# -------------------------------
# -------------------------------
# ACTION 5: Send Notifications (Upcoming exams/assignments)
# -------------------------------
class ActionGetAssignments(Action):
    def name(self):
        return "action_get_assignments"

    def run(self, dispatcher, tracker, domain):
        # Retrieve metadata from the latest message
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)
            print("User reg number:", user_reg_number)
            print("User role:", user_role)

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []

        course_code = tracker.get_slot('course_code')
        if not course_code:
            dispatcher.utter_message(text="Please specify the course code to get assignments.")
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT title, description FROM "Assignments" WHERE course_code = %s',
            (course_code,)
        )
        results = cursor.fetchall()

        if results:
            assignments = "\n\n".join(
                [f"📌 *{title}*:\n{description}" for title, description in results]
            )
            dispatcher.utter_message(
                text=f"Here are the assignments for course **{course_code}**:\n\n{assignments}"
            )
        else:
            dispatcher.utter_message(text=f"No assignments found for course **{course_code}**.")

        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]

class ActionScheduleAssignment(Action):
    def name(self):
        return "action_schedule_assignment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        metadata = tracker.latest_message.get('metadata', None)

        if metadata:
            user_reg_number = metadata.get('user_reg_number', None)
            user_role = metadata.get('user_role', None)
        else:
            user_reg_number = None
            user_role = None

        if not user_reg_number or not user_role:
            dispatcher.utter_message(text="Unable to retrieve user information.")
            return []

        if user_role != "faculty":
            dispatcher.utter_message(text="You are a student. You don't have access to schedule assignments.")
            return []

        # Retrieve slots
        course_code = tracker.get_slot('course_code')
        title = tracker.get_slot('assignment_title')
        description = tracker.get_slot('assignment_description')
        attachment_url = tracker.get_slot('attachment_url')
        due_date_str = tracker.get_slot('due_date')
        due_time_str = tracker.get_slot('due_time')

        print("Course code:", course_code)
        print("Title:", title)
        print("Description:", description)
        print("Attachment URL:", attachment_url)
        print("Due date:", due_date_str)
        print("Due time:", due_time_str)

        # Enforce no null attributes
        if not all([course_code, title, description, attachment_url, due_date_str, due_time_str]):
            dispatcher.utter_message(text="Please provide all required assignment details to schedule.")
            return []

        # Validate date and time format
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            due_time = datetime.strptime(due_time_str, '%H:%M').time()
        except ValueError:
            dispatcher.utter_message(text="Please provide the date in YYYY-MM-DD and time in HH:MM format.")
            return []

        # 🟢 Step 1: Get assigned_by UID using faculty reg_number
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT "UID" FROM "faculty_member_profiles" WHERE reg_number = %s',
            (user_reg_number,)
        )
        result = cursor.fetchone()
        if not result:
            dispatcher.utter_message(text="No faculty member found with the provided registration number.")
            return []

        assigned_by = result[0]  # UID

        # 🟢 Step 2: Prepare JSON payload
        payload = {
            "title": title,
            "course_code": course_code,
            "assigned_by": assigned_by,
            "description": description,
            "attachment_url": attachment_url,
            "notified": False,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "due_time": due_time.strftime("%H:%M:%S")
        }
        print("Payload for scheduling assignment:", payload)

        # 🟢 Step 3: Call the API to schedule assignment
        try:
            response = requests.post(f"{API_URL}/api/assignments/schedule", json=payload)

            if response.status_code == 200:
                dispatcher.utter_message(text=f"Assignment '{title}' scheduled successfully.")
            else:
                dispatcher.utter_message(text=f"Failed to schedule assignment. Server response: {response.text}")
        except Exception as e:
            dispatcher.utter_message(text=f"Error calling schedule API: {str(e)}")

        return [
            SlotSet("user_reg_number", user_reg_number),
            SlotSet("user_role", user_role)
        ]
