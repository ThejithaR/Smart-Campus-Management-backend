// attendanceRoutes.js
import express from "express";
import { manualAttendance, handleFaceRecognitionSocket, registerFace} from "../controllers/attendanceController.js";
// import { handleFaceRecognitionSocket } from '../controllers/attendanceController.js';
const attendenceRouter = express.Router();

export function setupWebSocketHandler(wss) {
  wss.on('connection', (ws, req) => {
    console.log('New WebSocket connection');
    handleFaceRecognitionSocket(ws); // pass to controller
  });
}


// define routes
attendenceRouter.post("/manual", manualAttendance); // Manual attendance route
attendenceRouter.post("/register-face", registerFace); // Register face route
export default attendenceRouter;   // <-- IMPORTANT
