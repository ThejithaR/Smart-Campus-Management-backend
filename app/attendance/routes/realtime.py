from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np

from services.face_service import recognize_faces

router = APIRouter(prefix="/realtime", tags=["realtime"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

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
        print(f"Error processing frame: {e}")
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

@router.websocket("/face-recognition")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            result = await process_frame(
                image_base64=data["image_base64"],
                threshold=float(data.get("threshold", 0.6)),
                location=data.get("location"),
                course_code=data.get("course_code")  # Extract course_code from request
            )
            
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket disconnected")
    except json.JSONDecodeError:
        await websocket.send_json({
            "success": False,
            "message": "Invalid JSON data received"
        })
    except KeyError:
        await websocket.send_json({
            "success": False,
            "message": "Missing required field 'image_base64'"
        })
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "success": False,
                "message": f"Server error: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket)
