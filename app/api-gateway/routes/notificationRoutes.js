import express from "express";
import {
  getNotifications,
  getNotificationDetails,
  addCourseNotification,
  addOneRecipientNotification,
  getAdminNotifications,
  getAdminNotificationDetails,
} from "../controllers/notificationController.js";

const notificationRouter = express.Router();

// Route to get notifications for a specific user
notificationRouter.get("/fetch-notifications-student/:userId", getNotifications);

// Route to get details of a specific notification (for students)
notificationRouter.get("/student-notification-details/:notificationId", getNotificationDetails);

// Route to add a notification (admin only)
notificationRouter.post("/add-notification-course", addCourseNotification);

notificationRouter.post("/add-notification-single", addOneRecipientNotification);

// Route to get notifications sent by an admin (faculty members)
notificationRouter.get("/fetch-notifications-admin/:facultyId", getAdminNotifications);

// Route to get details of a specific notification sent by an admin
notificationRouter.get("/admin-notification-details/:notificationId", getAdminNotificationDetails);

export default notificationRouter;