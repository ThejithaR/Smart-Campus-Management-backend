import {publishMessageWithReply} from "../services/rabbitmqService.js";
import {examCreateSchema, examUpdateSchema, assignmentCreateSchema, assignmentUpdateSchema} from "../models/scheduleManagerModels.js";

const QUEUE_NAME = "schedule_manager_queue";

export const scheduleAssignment = async (req, res) => {

    // Validate the request body against the schema
    const { error } = assignmentCreateSchema.validate(req.body);
    if (error) {
        console.error("Validation error:", error.details[0].message);
        return res.status(400).json({ error: error.details[0].message });
    }
    const { title, course_code, assigned_by, description, attachment_url, notified, due_date, due_time} = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "scheduleAssignment",
        payload:{
            title: title,
            course_code: course_code,
            assigned_by: assigned_by,
            description: description,
            attachment_url: attachment_url || null,
            notified: notified,
            due_date: due_date,
            due_time: due_time,
        },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Response from schedule assignment:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error assigning schedule:", error);
    res.status(500).json({ error: "Failed to assign schedule" });
  }
};


export const getAssignment = async (req, res) => {
  const { assignment_id } = req.body; // Assuming userId is sent in the request body
  const message = {
    action: "getAssignment",
    payload:{
        assignment_id: assignment_id,
    }
  };
  console.log("Message to be sent:", message); // Log the message being sent
  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Assignments:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error fetching assignments:", error);
    res.status(500).json({ error: "Failed to fetch assignments" });
  }
};

export const getAllAssignments = async (req, res) => {
    //const { course_code } = req.body; // Assuming userId is sent in the request body
    const message = {
        action: "getAllAssignments",
        // payload:{
        //     course_code: course_code,
        // }
    };
    console.log("Message to be sent:", message); // Log the message being sent
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Assignments:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error fetching assignments:", error);
        res.status(500).json({ error: "Failed to fetch assignments" });
    }
};

export const updateAssignment = async (req, res) => {

    // Validate the request body against the schema
    const { error } = assignmentUpdateSchema.validate(req.body);
    if (error) {
        console.error("Validation error:", error.details[0].message);
        return res.status(400).json({ error: error.details[0].message });
    }
    // Extract the necessary fields from the request body

    const { assignment_id, title, course_code, assigned_by, description, attachment_url, notified, due_date, due_time} = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "updateAssignment",
        payload:{
            assignment_id: assignment_id,
            assignment : {
                title: title,
                course_code: course_code,
                assigned_by: assigned_by,
                description: description,
                attachment_url: attachment_url || null,
                notified: notified,
                due_date: due_date,
                due_time: due_time,
            }
        },
    };
    
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Response from schedule assignment:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error assigning schedule:", error);
        res.status(500).json({ error: "Failed to assign schedule" });
    }
};

export const deleteAssignment = async (req, res) => {
    const { assignment_id } = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "deleteAssignment",
        payload:{
            assignment_id: assignment_id,
        },
    };
    
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Response from schedule assignment:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error assigning schedule:", error);
        res.status(500).json({ error: "Failed to assign schedule" });
    }
}


export const scheduleExam = async (req, res) => {

    // Validate the request body against the schema
    const { error } = examCreateSchema.validate(req.body);
    if (error) {
        console.error("Validation error:", error.details[0].message);
        return res.status(400).json({ error: error.details[0].message });
    }
    // Extract the necessary fields from the request body

    const { title, start_time, end_time, course_code, exam_date, notified, description, location, scheduled_by} = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "scheduleExam",
        payload:{
            exam:{
                title: title,
                start_time: start_time,
                end_time: end_time,
                course_code: course_code,
                exam_date: exam_date,
                notified: bool = notified,
                description: description,
                location: location,
                scheduled_by: scheduled_by,
                course_code: course_code,
            }
        },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Response from schedule assignment:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error assigning schedule:", error);
    res.status(500).json({ error: "Failed to assign schedule" });
  }
}

export const getExam = async (req, res) => {
    const { exam_id } = req.body; // Assuming userId is sent in the request body
    const message = {
        action: "getExam",
        payload:{
            exam_id: exam_id,
        }
    };
    console.log("Message to be sent:", message); // Log the message being sent
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Assignments:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error fetching assignments:", error);
        res.status(500).json({ error: "Failed to fetch assignments" });
    }
}

export const getAllExams = async (req, res) => {
    //const { course_code } = req.body; // Assuming userId is sent in the request body
    const message = {
        action: "getAllExams",
        // payload:{
        //     course_code: course_code,
        // }
    };
    console.log("Message to be sent:", message); // Log the message being sent
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Assignments:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error fetching assignments:", error);
        res.status(500).json({ error: "Failed to fetch assignments" });
    }
}

export const updateExam = async (req, res) => {
    // Validate the request body against the schema
    const { error } = examUpdateSchema.validate(req.body);
    if (error) {
        console.error("Validation error:", error.details[0].message);
        return res.status(400).json({ error: error.details[0].message });
    }
    // Extract the necessary fields from the request body

    const { exam_id, title, start_time, end_time, course_code, exam_date, notified, description, location, scheduled_by} = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "updateExam",
        payload:{
            exam_id: exam_id,
            exam : {
                title: title,
                start_time: start_time,
                end_time: end_time,
                course_code: course_code,
                exam_date: exam_date,
                notified: bool = notified,
                description: description,
                location: location,
                scheduled_by: scheduled_by,
                course_code: course_code,
            }
        },
  };

  try {
    const response = await publishMessageWithReply(QUEUE_NAME, message);
    console.log("Response from schedule assignment:", response); // Log the response for debugging
    res.status(200).json(response);
  } catch (error) {
    console.error("Error assigning schedule:", error);
    res.status(500).json({ error: "Failed to assign schedule" });
  }
}

export const deleteExam = async (req, res) => {
    const { exam_id } = req.body; // Assuming userId and courseId are sent in the request body
    console.log("Request body:", req.body); // Log the request body for debugging
    const message = {
        action: "deleteExam",
        payload:{
            exam_id: exam_id,
        },
    };
    
    try {
        const response = await publishMessageWithReply(QUEUE_NAME, message);
        console.log("Response from schedule assignment:", response); // Log the response for debugging
        res.status(200).json(response);
    } catch (error) {
        console.error("Error assigning schedule:", error);
        res.status(500).json({ error: "Failed to assign schedule" });
    }
}