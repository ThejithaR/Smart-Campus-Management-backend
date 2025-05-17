import numpy as np
import base64
import cv2
from typing import List, Dict, Any, Optional, Tuple
import json
from io import BytesIO
from PIL import Image
from db.supabase import get_all_face_embeddings, save_face_embedding, log_attendance, get_student_profile
import face_recognition
from services.attendace_logic import can_mark_attendance,can_mark_attendance_for_course
from datetime import datetime


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode a base64 image string to a numpy array
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        numpy array representing the image
    """
    # Remove the data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
        
    image_data = base64.b64decode(base64_string)
    
    # Use PIL to open the image
    image = Image.open(BytesIO(image_data))
    
    # Convert to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')
        
    # Convert to numpy array
    return np.array(image)


def extract_face_embedding(image: np.ndarray) -> Tuple[List[float], List[List[int]]]:
    """
    Extract face embedding from an image
    
    Args:
        image: Image as numpy array
        
    Returns:
        Tuple of (list of face embeddings, list of face locations)
    """
    # Find face locations in the image
    face_locations = face_recognition.face_locations(image)
    
    # If no faces found, return empty lists
    if not face_locations:
        return [], []
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    # Convert numpy arrays to lists for JSON serialization
    return [encoding.tolist() for encoding in face_encodings], face_locations


def register_face(reg_number: str, image_base64: str) -> Dict[str, Any]:
    """
    Register a face for a student
    
    Args:
        reg_number: Student registration number
        image_base64: Base64 encoded image
        
    Returns:
        Dictionary with operation result
    """
    try:
        # Get student profile first to ensure student exists
        student = get_student_profile(reg_number)
        if not student["success"]:
            return {"success": False, "message": "Student not found"}
        
        # Decode image
        image = decode_base64_image(image_base64)
        
        # Extract face embedding
        face_embeddings, face_locations = extract_face_embedding(image)
        
        if not face_embeddings:
            return {"success": False, "message": "No face detected in the image"}
        
        if len(face_embeddings) > 1:
            return {"success": False, "message": "Multiple faces detected. Please provide an image with only one face."}
        
        # Save face embedding
        result = save_face_embedding(
            reg_number=reg_number,
            embedding=face_embeddings[0],
            name=student["data"].get("name")
        )
        
        return result
    except Exception as e:
        print(f"Error registering face: {e}")
        return {"success": False, "message": str(e)}
    

def recognize_faces(image_base64: str, location: Optional[str] = None, 
                   course_code: Optional[str] = None, threshold: float = 0.6,) -> Dict[str, Any]:
    """
    Recognize faces in an image and mark attendance based on course schedule
    
    Args:
        image_base64: Base64 encoded image
        location: Optional location information for attendance logging
        threshold: Similarity threshold (lower is more strict)
        course_code: Optional course code for attendance
        
    Returns:
        Dictionary with recognized students
    """
    try:
        # Decode image
        image = decode_base64_image(image_base64)
        
        # Extract face embedding
        face_embeddings, face_locations = extract_face_embedding(image)
        
        if not face_embeddings:
            return {"success": False, "message": "No face detected in the image", "students": []}
        
        # Get all stored face embeddings
        stored_embeddings = get_all_face_embeddings()
        #print(f"Stored embeddings: {stored_embeddings}")
        if not stored_embeddings:
            return {"success": False, "message": "No registered faces found in the database", "students": []}
        
        recognized_students = []
        unknown_faces = []
        attendance_results = []
        
        # Current time for attendance checking
        current_time = datetime.now()
        
        for i, face_embedding in enumerate(face_embeddings):
            best_match = None
            best_similarity = -1
            
            for stored_record in stored_embeddings:
                stored_embedding = stored_record["embedding"]
                
                similarity = face_recognition.face_distance([np.array(stored_embedding)], np.array(face_embedding))
                similarity = 1 - similarity[0]
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = stored_record
            
            if best_match and best_similarity > threshold:
                confidence = round(best_similarity * 100, 2)
                reg_number = best_match["reg_number"]
                
                # Check attendance eligibility based on course schedule
                if course_code:
                    # Use the new course-based attendance logic
                    attendance_check = can_mark_attendance_for_course(
                        reg_number=reg_number,
                        course_code=course_code,
                        current_time=current_time
                    )
                else:
                    # Fallback to the original attendance logic when no course is specified
                    attendance_check = can_mark_attendance(reg_number)
                
                # Format the attendance status message
                if attendance_check.get("can_mark", False):
                    status = attendance_check.get("status", "present")
                    attendance_status = f"Can mark as {status}" if status else "Can mark attendance"
                else:
                    attendance_status = attendance_check.get("message", "Cannot mark attendance")
                
                recognized_student = {
                    "reg_number": reg_number,
                    "name": best_match["name"],
                    "confidence": confidence,
                    "can_mark_attendance": attendance_check.get("can_mark", False),
                    "attendance_message": attendance_check.get("message", ""),
                    "attendance_status": attendance_status,
                    "face_location": face_locations[i] if i < len(face_locations) else None
                }
                
                recognized_students.append(recognized_student)
                
                # Mark attendance if eligible
                if attendance_check.get("can_mark", False):
                    # Use the determined status (present/late) for logging
                    status = attendance_check.get("status", "present")
                    
                    attendance_result = log_attendance(
                        reg_number=reg_number,
                        method="face_recognition",  # Using your original default
                        status=status,  # Use the status from attendance check (present/late)
                        location=location,
                        course_code=course_code
                    )
                    attendance_results.append({
                        "reg_number": reg_number,
                        "name": best_match.get("name", "Unknown"),
                        "status": status,
                        "attendance_result": attendance_result
                    })
            else:
                unknown_faces.append({
                    "face_index": i,
                    "location": face_locations[i] if i < len(face_locations) else None,
                    "confidence": round(best_similarity * 100, 2) if best_match else 0,
                    "best_match_name": best_match["name"] if best_match else None,
                    "message": "Unknown person - below recognition threshold"
                })
        
        response = {
            "success": True,
            "total_faces_detected": len(face_embeddings),
            "recognized_count": len(recognized_students),
            "unknown_count": len(unknown_faces),
            "students": recognized_students,
            "unknown_faces": unknown_faces,
            "attendance_results": attendance_results
        }
        
        if len(recognized_students) > 0:
            response["message"] = f"Recognized {len(recognized_students)} student(s)"
            if len(unknown_faces) > 0:
                response["message"] += f" and detected {len(unknown_faces)} unknown face(s)"
        elif len(unknown_faces) > 0:
            response["message"] = f"Detected {len(unknown_faces)} face(s), but none matched registered students"
            response["success"] = False
        else:
            response["message"] = "No registered students recognized in the image"
            response["success"] = False
            
        return response
        
    except Exception as e:
        print(f"Error recognizing faces: {e}")
        return {
            "success": False, 
            "message": str(e), 
            "students": [],
            "unknown_faces": [],
            "attendance_results": []
        }
    
# def recognize_faces(image_base64: str, location: Optional[str] = None, 
#                     threshold: float = 0.6, course_code: Optional[str] = None) -> Dict[str, Any]:
#     """
#     Recognize faces in an image
    
#     Args:
#         image_base64: Base64 encoded image
#         location: Optional location information for attendance logging
#         threshold: Similarity threshold (lower is more strict)
#         course_code: Optional course code for attendance
        
#     Returns:
#         Dictionary with recognized students
#     """
#     try:
#         # Decode image
#         image = decode_base64_image(image_base64)
        
#         # Extract face embedding
#         face_embeddings, face_locations = extract_face_embedding(image)
        
#         if not face_embeddings:
#             return {"success": False, "message": "No face detected in the image", "students": []}
        
#         # Get all stored face embeddings
#         stored_embeddings = get_all_face_embeddings()
        
#         if not stored_embeddings:
#             return {"success": False, "message": "No registered faces found in the database", "students": []}
        
#         recognized_students = []
#         unknown_faces = []
#         attendance_results = []
        
#         for i, face_embedding in enumerate(face_embeddings):
#             best_match = None
#             best_similarity = -1
            
#             for stored_record in stored_embeddings:
#                 stored_embedding = stored_record["embedding"]
                
#                 similarity = face_recognition.face_distance([np.array(stored_embedding)], np.array(face_embedding))
#                 similarity = 1 - similarity[0]
                
#                 if similarity > best_similarity:
#                     best_similarity = similarity
#                     best_match = stored_record
            
#             if best_match and best_similarity > threshold:
#                 confidence = round(best_similarity * 100, 2)
#                 reg_number = best_match["reg_number"]
                
#                 attendance_check = can_mark_attendance(reg_number)
#                 attendance_status = "Attendance Taken" if attendance_check["can_mark"] else "Attendance Already Taken"
                
#                 recognized_student = {
#                     "reg_number": reg_number,
#                     "name": best_match["name"],
#                     "confidence": confidence,
#                     "can_mark_attendance": attendance_check["can_mark"],
#                     "attendance_message": attendance_check["message"],
#                     "attendance_status": attendance_status,
#                     "face_location": face_locations[i] if i < len(face_locations) else None
#                 }
                
#                 recognized_students.append(recognized_student)
                
#                 if attendance_check["can_mark"]:
#                     attendance_result = log_attendance(
#                         reg_number=reg_number,
#                         method="facial recognition",
#                         status="present",
#                         location=location,
#                         course_code=course_code  # <-- Pass course_code here
#                     )
#                     attendance_results.append({
#                         "reg_number": reg_number,
#                         "name": best_match.get("name", "Unknown"),
#                         "attendance_result": attendance_result
#                     })
#             else:
#                 unknown_faces.append({
#                     "face_index": i,
#                     "location": face_locations[i] if i < len(face_locations) else None,
#                     "confidence": round(best_similarity * 100, 2) if best_match else 0,
#                     "best_match_name": best_match["name"] if best_match else None,
#                     "message": "Unknown person - below recognition threshold"
#                 })
        
#         response = {
#             "success": True,
#             "total_faces_detected": len(face_embeddings),
#             "recognized_count": len(recognized_students),
#             "unknown_count": len(unknown_faces),
#             "students": recognized_students,
#             "unknown_faces": unknown_faces,
#             "attendance_results": attendance_results
#         }
        
#         if len(recognized_students) > 0:
#             response["message"] = f"Recognized {len(recognized_students)} student(s)"
#             if len(unknown_faces) > 0:
#                 response["message"] += f" and detected {len(unknown_faces)} unknown face(s)"
#         elif len(unknown_faces) > 0:
#             response["message"] = f"Detected {len(unknown_faces)} face(s), but none matched registered students"
#             response["success"] = False
#         else:
#             response["message"] = "No registered students recognized in the image"
#             response["success"] = False
            
#         return response
        
#     except Exception as e:
#         print(f"Error recognizing faces: {e}")
#         return {
#             "success": False, 
#             "message": str(e), 
#             "students": [],
#             "unknown_faces": [],
#             "attendance_results": []
#         }
