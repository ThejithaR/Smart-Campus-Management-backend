// attendanceRoutes.js
import express from "express";
import { scheduleAssignment, getAssignment, getAllAssignments, updateAssignment, deleteAssignment } from "../controllers/scheduleManagerController.js";
const scheduleManagerRouter = express.Router();

// define routes
scheduleManagerRouter.get("/", (req, res) => {
  res.send("Schedule manager Home");
});

scheduleManagerRouter.post("/schedule-assignment", scheduleAssignment);
scheduleManagerRouter.post("/get-assignment", getAssignment);
scheduleManagerRouter.get("/get-all-assignments", getAllAssignments);
scheduleManagerRouter.put("/update-assignment", updateAssignment);
scheduleManagerRouter.delete("/delete-assignment", deleteAssignment);


export default scheduleManagerRouter;   // <-- IMPORTANT
