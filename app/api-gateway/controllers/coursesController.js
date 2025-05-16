import {publishMessageWithReply} from "../services/rabbitmqService.js";

const QUEUE_NAME = "courses_queue";

export const getEnrolledCourses = async (req, res) => {
  console.log("Request body:", req.body); // Log the request body for debugging  
  const { reg_number } = req.body; // Assuming userId is sent in the request body
  const message = {
    action: "getEnrolledCourses",
    payload:{
        reg_number: reg_number,
    }
  };
  console.log("Message to be sent:", message); // Log the message being sent
  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Enrolled courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching enrolled courses:", error);
    res.status(500).json({ error: "Failed to fetch enrolled courses" });
  }
}

export const getEligibleCourses = async (req, res) => {
  const { reg_number } = req.body; // Assuming userId is sent in the request body
  const message = {
    action: "getEligibleCourses",
    payload:{
        reg_number: reg_number,
    }
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Eligible courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching eligible courses:", error);
    res.status(500).json({ error: "Failed to fetch eligible courses" });
  }
}

export const getEligibleCoursesYetToEnroll = async (req, res) => {
  const { reg_number } = req.body; // Assuming userId is sent in the request body
  const message = {
    action: "getEligibleCoursesYetTooEnroll",
    payload:{
        reg_number: reg_number,
    }
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Eligible courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching eligible courses:", error);
    res.status(500).json({ error: "Failed to fetch eligible courses" });
  }
}

export const enrollInCourse = async (req, res) => {
  const { reg_number, course_id } = req.body; // Assuming userId and courseId are sent in the request body
  print("Request body:", req.body); // Log the request body for debugging
  const message = {
    action: "enrollInCourse",
    payload:{
        reg_number: reg_number,
        course_id: course_id,
    },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Response from course enrollment:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error enrolling in course:", error);
    res.status(500).json({ error: "Failed to enroll in course" });
  }
}

export const unenrollFromCourse = async (req, res) => {
  const { reg_number, course_id } = req.body; // Assuming userId and courseId are sent in the request body
  const message = {
    action: "unenrollFromCourse",
    payload:{
        reg_number: reg_number,
        course_id: course_id,
    },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    res.status(200).json(response);
  } catch (error) {
    console.error("Error unenrolling from course:", error);
    res.status(500).json({ error: "Failed to unenroll from course" });
  }
}

export const getAssignedCourses = async (req, res) => {
  const { reg_number } = req.body; // Assuming userId is sent in the request body
  const message = {
    action: "getAssignedCourses",
    payload:{
        reg_number: reg_number,
    }
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Assigned courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching assigned courses:", error);
    res.status(500).json({ error: "Failed to fetch assigned courses" });
  }
}

export const getAllCourses = async (req, res) => {
  const message = {
    action: "getAllCourses",
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("All courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching all courses:", error);
    res.status(500).json({ error: "Failed to fetch all courses" });
  }
}

export const getAllCoursesYetToAssign = async (req, res) => {
  const message = {
    action: "getAllCoursesYetToAssign",
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("All courses:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching all courses:", error);
    res.status(500).json({ error: "Failed to fetch all courses" });
  }
}

export const addNewCourse = async (req, res) => {
  const { course_id, course_name, course_description } = req.body; // Assuming userId and courseId are sent in the request body
  console.log("Request body:", req.body); // Log the request body for debugging
  const message = {
    action: "addNewCourse",
    payload:{
        course_id: course_id,
        course_name: course_name,
        course_description: course_description,
    },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    res.status(200).json(response);
  } catch (error) {
    console.error("Error adding new course:", error);
    res.status(500).json({ error: "Failed to add new course" });
  }
}

export const getLecturers = async (req, res) => {

  console.log("Request Get lecturers"); // Log the request body for debugging
  const message = {
    action: "getLecturers",
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("All lecturers:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching all lecturers:", error);
    res.status(500).json({ error: "Failed to fetch all lecturers" });
  }
}