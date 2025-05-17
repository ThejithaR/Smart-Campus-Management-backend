from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from db.supabase import get_attendance_today,get_course_details,get_student_course_attendance_today

def can_mark_attendance(reg_number: str, attendance_window_hours: int = 2) -> Dict[str, Any]:
    """
    Check if a student can mark attendance based on their last attendance record
    
    Args:
        reg_number: Student registration number
        attendance_window_hours: Time window in hours before allowing a new attendance record
        
    Returns:
        Dictionary with result indicating if attendance can be marked
    """
    try:
        # Get today's attendance records for the student
        result = get_attendance_today(reg_number)
        
        if not result["success"]:
            return {"can_mark": False, "message": f"Error checking attendance: {result['message']}"}
        
        attendance_records = result["data"]
        
        # If no records found today, student can mark attendance
        if not attendance_records:
            return {"can_mark": True, "message": "No previous attendance record today"}
        
        # Get the latest attendance record
        latest_record = max(attendance_records, key=lambda x: x.get("timestamp", ""))
        
        # Parse the timestamp
        try:
            # Make sure to handle timezone properly
            if isinstance(latest_record["timestamp"], str):
                # Handle various timestamp formats
                timestamp_str = latest_record["timestamp"]
                # Remove 'Z' if present and add UTC indicator
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1] + '+00:00'
                # Ensure timezone info is included
                elif '+' not in timestamp_str and '-' not in timestamp_str[10:]:
                    timestamp_str += '+00:00'
                
                latest_timestamp = datetime.fromisoformat(timestamp_str)
            else:
                # If it's already a datetime object
                latest_timestamp = latest_record["timestamp"]
                
        except (ValueError, KeyError) as e:
            print(f"Error parsing timestamp: {e}")
            # If we can't parse the timestamp, allow marking attendance but log the issue
            return {"can_mark": True, "message": f"Unable to parse previous attendance timestamp: {e}"}
        
        # Get current time in the same timezone as latest_timestamp
        if latest_timestamp.tzinfo:
            current_time = datetime.now(latest_timestamp.tzinfo)
        else:
            current_time = datetime.now()
        
        # Check if the time difference is greater than the window
        time_diff = current_time - latest_timestamp
        
        # Debug print
        print(f"Time difference: {time_diff.total_seconds()} seconds")
        print(f"Attendance window: {attendance_window_hours * 3600} seconds")
        
        if time_diff.total_seconds() < attendance_window_hours * 3600:
            # Calculate when they can mark attendance again
            next_allowed_time = latest_timestamp + timedelta(hours=attendance_window_hours)
            time_remaining = next_allowed_time - current_time
            minutes_remaining = max(1, int(time_remaining.total_seconds() / 60))
            
            return {
                "can_mark": False,
                "message": f"Attendance already marked. Can mark again in {minutes_remaining} minutes",
                "last_marked": latest_timestamp.isoformat(),
                "next_allowed": next_allowed_time.isoformat()
            }
        
        return {"can_mark": True, "message": "Can mark attendance"}
    
    except Exception as e:
        import traceback
        print(f"Error checking if attendance can be marked: {e}")
        print(traceback.format_exc())
        return {"can_mark": False, "message": f"Error: {str(e)}"}  

def can_mark_attendance_for_course(
    reg_number: str, 
    course_code: str = None,
    current_time: datetime = None
) -> Dict[str, Any]:
    """
    Check if a student can mark attendance based on course schedule and previous attendance
    
    Args:
        reg_number: Student registration number
        course_code: Course code to check attendance for
        current_time: Current time (defaults to now if not provided)
        
    Returns:
        Dictionary with result indicating if attendance can be marked and status
    """
    try:
        if not current_time:
            current_time = datetime.now()
            
        # If no course code provided, cannot check course-specific attendance
        if not course_code:
            return {
                "can_mark": False, 
                "status": None,
                "message": "No course code provided"
            }
            
        # Get today's day of week
        day_of_week = current_time.strftime("%A")  # Returns Monday, Tuesday, etc.
        
        # Get course schedule for the given course code
        course_details = get_course_details(course_code)
        if not course_details["success"]:
            return {
                "can_mark": False,
                "status": None,
                "message": f"Error fetching course details: {course_details['message']}"
            }
            
        # Check if course is scheduled for today
        if course_details["data"]["day_of_week"] != day_of_week:
            return {
                "can_mark": False,
                "status": None,
                "message": f"Course {course_code} is not scheduled for today ({day_of_week})"
            }
            
        # Parse course start and end times
        start_time_str = course_details["data"]["start_time"]
        end_time_str = course_details["data"]["end_time"]
        
        # Create datetime objects for today's course start and end times
        course_date = current_time.date()
        
        # Handle time format (assuming HH:MM:SS format, but being flexible)
        if isinstance(start_time_str, str):
            if ":" in start_time_str:
                # Handle different time formats
                if start_time_str.count(":") == 1:  # HH:MM
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                else:  # HH:MM:SS
                    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
            else:
                # If it's just a number of seconds or other format
                print(f"Warning: Unexpected time format: {start_time_str}")
                return {
                    "can_mark": False,
                    "status": None,
                    "message": f"Invalid time format for course start time: {start_time_str}"
                }
        else:
            # If it's already a time object
            start_time = start_time_str
            
        # Same for end time
        if isinstance(end_time_str, str):
            if ":" in end_time_str:
                if end_time_str.count(":") == 1:  # HH:MM
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()
                else:  # HH:MM:SS
                    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
            else:
                print(f"Warning: Unexpected time format: {end_time_str}")
                return {
                    "can_mark": False,
                    "status": None,
                    "message": f"Invalid time format for course end time: {end_time_str}"
                }
        else:
            end_time = end_time_str
            
        course_start = datetime.combine(course_date, start_time)
        course_end = datetime.combine(course_date, end_time)
        
        # Check if student has already marked attendance for this course today
        attendance_today = get_student_course_attendance_today(reg_number, course_code)
        if not attendance_today["success"]:
            return {
                "can_mark": False,
                "status": None,
                "message": f"Error checking attendance: {attendance_today['message']}"
            }
            
        if attendance_today["data"]:
            # Student has already marked attendance for this course today
            return {
                "can_mark": False,
                "status": None,
                "message": "Attendance already marked for this course today",
                "last_marked": attendance_today["data"][0]["timestamp"]
            }
            
        # Define time windows
        one_hour_before_start = course_start - timedelta(hours=1)
        one_hour_after_start = course_start + timedelta(hours=1)
        
        # Determine attendance status based on current time
        if one_hour_before_start <= current_time < course_start:
            # Within one hour before course starts - mark as "present"
            return {
                "can_mark": True,
                "status": "present",
                "message": "Can mark attendance as present"
            }
        elif course_start <= current_time < one_hour_after_start:
            # Within one hour after course starts - also mark as "present"
            return {
                "can_mark": True,
                "status": "present",
                "message": "Can mark attendance as present"
            }
        elif one_hour_after_start <= current_time < course_end:
            # After one hour from start but before end - mark as "late"
            return {
                "can_mark": True,
                "status": "late",
                "message": "Can mark attendance as late"
            }
        else:
            # Outside valid attendance windows
            if current_time < one_hour_before_start:
                return {
                    "can_mark": False,
                    "status": None,
                    "message": f"Too early to mark attendance. Course starts at {start_time_str}"
                }
            else:
                return {
                    "can_mark": False,
                    "status": None,
                    "message": f"Too late to mark attendance. Course ended at {end_time_str}"
                }
    
    except Exception as e:
        import traceback
        print(f"Error checking if attendance can be marked for course: {e}")
        print(traceback.format_exc())
        return {"can_mark": False, "status": None, "message": f"Error: {str(e)}"}

def get_attendance_stats(reg_number: str, days: int = 30) -> Dict[str, Any]:
    """
    Get attendance statistics for a student
    
    Args:
        reg_number: Student registration number
        days: Number of past days to include in statistics
        
    Returns:
        Dictionary with attendance statistics
    """
    from db.supabase import get_student_attendance_report
    from datetime import datetime, timedelta
    
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        result = get_student_attendance_report(reg_number, start_date, end_date)
        
        if not result["success"]:
            return {"success": False, "message": result["message"]}
        
        records = result["data"]
        
        # Initialize counters
        stats = {
            "total": len(records),
            "present": 0,
            "absent": 0,
            "late": 0,
            "attendance_rate": 0.0,
            "attendance_by_date": {}
        }
        
        # Count by status
        for record in records:
            status = record.get("status", "")
            record_date = record.get("timestamp", "")[:10]  # Extract date part
            
            if status == "present":
                stats["present"] += 1
            elif status == "absent":
                stats["absent"] += 1
            elif status == "late":
                stats["late"] += 1
                
            # Group by date
            if record_date not in stats["attendance_by_date"]:
                stats["attendance_by_date"][record_date] = []
            
            stats["attendance_by_date"][record_date].append(record)
        
        # Calculate attendance rate
        if stats["total"] > 0:
            stats["attendance_rate"] = round((stats["present"] + stats["late"]) / stats["total"] * 100, 2)
            
        return {"success": True, "data": stats}
    
    except Exception as e:
        print(f"Error getting attendance stats: {e}")
        return {"success": False, "message": str(e)}

def mark_student_absent(course_code: str, date_value: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Mark students as absent for a course on a specific date if they haven't marked attendance
    
    Args:
        course_code: The course code
        date_value: The date for which to mark absences (default: today)
        
    Returns:
        Dictionary with operation result
    """
    from db.supabase import get_course_attendance_report, log_attendance
    
    try:
        if not date_value:
            date_value = datetime.now().date()
            
        # Get all enrolled students and their attendance for the course
        result = get_course_attendance_report(course_code, date_value)
        
        if not result["success"]:
            return {"success": False, "message": result["message"]}
            
        attendance_data = result["data"]
        
        # Create a set of students who have already marked attendance
        students_with_attendance = {record["reg_number"] for record in attendance_data}
        
        # Get all enrolled students
        from db.supabase import supabase
        enrollments = supabase.table("Enrollments") \
                     .select("Enrollments.reg_number, Student profiles.name") \
                     .eq("course_code", course_code) \
                     .join("Student profiles", "Student profiles.reg_number=Enrollments.reg_number") \
                     .execute()
                     
        if not enrollments.data:
            return {"success": False, "message": "No students enrolled in this course"}
            
        # Mark absent for students who haven't marked attendance
        absent_count = 0
        for enrollment in enrollments.data:
            reg_number = enrollment["reg_number"]
            
            if reg_number not in students_with_attendance:
                # Log absence
                log_attendance(
                    reg_number=reg_number,
                    method="automatic",
                    status="absent"
                )
                absent_count += 1
                
        return {
            "success": True, 
            "message": f"Marked {absent_count} students absent for course {course_code}",
            "data": {"absent_count": absent_count}
        }
        
    except Exception as e:
        print(f"Error marking students absent: {e}")
        return {"success": False, "message": str(e)}