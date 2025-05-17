// attendanceRoutes.js
import express from "express";
import { getEnrolledCourses, getEligibleCourses, getAssignedCourses, getAllCourses, enrollInCourse, unenrollFromCourse, getLecturers, addNewCourse, getEligibleCoursesYetToEnroll, getAllCoursesYetToAssign} from "../controllers/coursesController.js";
const courseEnrollmentRouter = express.Router();

// define routes
courseEnrollmentRouter.get("/", (req, res) => {
  res.send("Coursse enrollments Home");
});

courseEnrollmentRouter.post("/enrolled", getEnrolledCourses)
courseEnrollmentRouter.post("/eligible", getEligibleCourses)
courseEnrollmentRouter.post("/assigned", getAssignedCourses)
courseEnrollmentRouter.get("/all", getAllCourses)
courseEnrollmentRouter.post("/enroll", enrollInCourse)
courseEnrollmentRouter.post("/unenroll", unenrollFromCourse)
courseEnrollmentRouter.get("/lecturers", getLecturers)
courseEnrollmentRouter.post("/add-new-course", addNewCourse)
courseEnrollmentRouter.post("/eligible-yet-to-enroll", getEligibleCoursesYetToEnroll)
courseEnrollmentRouter.post("/all-yet-to-assign", getAllCoursesYetToAssign)

export default courseEnrollmentRouter;   // <-- IMPORTANT
