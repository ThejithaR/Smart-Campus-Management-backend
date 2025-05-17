from typing import Dict, Any, Optional
from services.face_service import recognize_faces

async def process_frame(image_base64: str, threshold: float = 0.6,
                        location: Optional[str] = None,
                        course_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a frame using the recognize_faces function
    """
    try:
        result = recognize_faces(
            image_base64=image_base64,
            location=location,
            threshold=threshold,
            course_code=course_code
        )

        return {
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "students": result.get("students", []),
            "unknown_faces": result.get("unknown_faces", []),
            "attendance_results": result.get("attendance_results", []),
            "total_faces_detected": len(result.get("students", [])) + len(result.get("unknown_faces", [])),
            "recognized_count": len(result.get("students", [])),
            "unknown_count": len(result.get("unknown_faces", []))
        }

    except Exception as e:
        print(f"[Realtime Controller] Error processing frame: {e}")
        return {
            "success": False,
            "message": str(e),
            "students": [],
            "unknown_faces": [],
            "attendance_results": [],
            "total_faces_detected": 0,
            "recognized_count": 0,
            "unknown_count": 0
        }

async def handle_realtime_message(action: str, data: dict) -> dict:
    """
    Dispatcher for RabbitMQ realtime messages.
    """
    if action == "faceRecognition":
        result =  await process_frame(
            image_base64=data.get("image_base64"),
            threshold=float(data.get("threshold", 0.6)),
            location=data.get("location"),
            course_code=data.get("course_code")
        )
        print(f"[Realtime Controller] Face recognition result: {result}")
        return result
    else:
        return {
            "success": False,
            "message": f"Unknown action: {action}"
        }
