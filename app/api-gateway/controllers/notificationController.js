import { publishMessageWithReply } from "../services/rabbitmqService.js";

const QUEUE_NAME = "notifications_queue";

// Get notifications for a specific user
export const getNotifications = async (req, res) => {
  const { userId } = req.params;

  console.log("params", req.params);
  if (!userId) {
    return res.status(400).json({ success: false, message: "User ID is required" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "getNotifications",
      payload: { userId },
    });

    res.status(200).json({ success: true, notifications: response });
  } catch (error) {
    console.error("GetNotifications Error:", error);
    res.status(500).json({ success: false, message: "Failed to fetch notifications" });
  }
};

// Get details of a specific notification (for students)
export const getNotificationDetails = async (req, res) => {
  const { notificationId } = req.params;

  console.log("params", req.params);

  if (!notificationId) {
    return res.status(400).json({ success: false, message: "Notification ID is required" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "getNotificationDetails",
      payload: { notificationId },
    });

    res.status(200).json({ success: true, notification: response });
  } catch (error) {
    console.error("GetNotificationDetails Error:", error);
    res.status(500).json({ success: false, message: "Failed to fetch notification details" });
  }
};

// Add a notification (admin only)
export const addCourseNotification = async (req, res) => {
  const { 
    course_code, 
    sender_id, 
    title, 
    message } = req.body;

  console.log("body", req.body);

  if (!title || !message || !course_code || !sender_id) {
    return res.status(400).json({ success: false, message: "All fields are required: Title, Message, Priority, Course_Code, Sent_By" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "addCourseNotification",
      payload: { title, message, course_code, sender_id },
    });

    res.status(201).json({ success: true, message: "Notification added successfully", notification: response });
  } catch (error) {
    console.error("AddNotification Error:", error);
    res.status(500).json({ success: false, message: "Failed to add notification" });
  }
};

export const addOneRecipientNotification = async (req, res) => {
  const { 
    course_code, 
    sender_id, 
    title, 
    message,
    recipient_id } = req.body;

  console.log("body", req.body);

  if (!title || !message || !course_code || !sender_id || !recipient_id) {
    return res.status(400).json({ success: false, message: "All fields are required: Title, Message, Priority, Course_Code, Sent_By" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "addOneRecipientNotification",
      payload: { title, message, course_code, sender_id, recipient_id },
    });

    res.status(201).json({ success: true, message: "Notification added successfully", notification: response });
  } catch (error) {
    console.error("AddNotification Error:", error);
    res.status(500).json({ success: false, message: "Failed to add notification" });
  }
}

// Get notifications sent by an admin (faculty members)
export const getAdminNotifications = async (req, res) => {
  const { facultyId } = req.params;

  console.log("params", req.params);

  if (!facultyId) {
    return res.status(400).json({ success: false, message: "Faculty ID is required" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "getAdminNotifications",
      payload: { facultyId },
    });

    res.status(200).json({ success: true, notifications: response });
  } catch (error) {
    console.error("GetAdminNotifications Error:", error);
    res.status(500).json({ success: false, message: "Failed to fetch admin notifications" });
  }
};

// Get details of a specific notification sent by an admin
export const getAdminNotificationDetails = async (req, res) => {
  const { notificationId } = req.params;

  console.log("params", req.params);

  if (!notificationId) {
    return res.status(400).json({ success: false, message: "Notification ID is required" });
  }

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "getAdminNotificationDetails",
      payload: { notificationId },
    });

    res.status(200).json({ success: true, notification: response });
  } catch (error) {
    console.error("GetAdminNotificationDetails Error:", error);
    res.status(500).json({ success: false, message: "Failed to fetch admin notification details" });
  }
};