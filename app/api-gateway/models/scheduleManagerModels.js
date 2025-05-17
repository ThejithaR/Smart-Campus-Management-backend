import Joi from "joi";
import { v4 as uuidv4 } from "uuid";


// AssignmentCreateRequest Schema
export const assignmentCreateSchema = Joi.object({
  title: Joi.string().required(),
  course_code: Joi.string().required(),
  assigned_by: Joi.string()
    .guid({ version: 'uuidv4' })
    .required(),
  description: Joi.string().required(),
  attachment_url: Joi.string().uri().optional(),
  notified: Joi.boolean().default(false),
  due_date: Joi.date().required(),
  due_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).required() // "HH:MM"
});

// AssignmentUpdateRequest Schema
export const assignmentUpdateSchema = Joi.object({
  title: Joi.string().optional(),
  course_code: Joi.string().optional(),
  assigned_by: Joi.string()
    .guid({ version: 'uuidv4' })
    .optional(),
  description: Joi.string().optional(),
  attachment_url: Joi.string().uri().optional(),
  notified: Joi.boolean().optional(),
  due_date: Joi.date().optional(),
  due_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).optional()
});

// ExamCreateRequest Schema
export const examCreateSchema = Joi.object({
  title: Joi.string().required(),
  start_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).required(), // Format: "HH:MM"
  end_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).required(),
  course_code: Joi.string().required(),
  exam_date: Joi.date().required(),
  notified: Joi.boolean().default(false),
  description: Joi.string().required(),
  location: Joi.string().required(),
  scheduled_by: Joi.string()
    .guid({ version: 'uuidv4' })
    .required()
});

// ExamUpdateRequest Schema
export const examUpdateSchema = Joi.object({
  title: Joi.string().optional(),
  start_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).optional(),
  end_time: Joi.string().regex(/^([0-1]\d|2[0-3]):([0-5]\d)$/).optional(),
  exam_date: Joi.date().optional(),
  notified: Joi.boolean().optional(),
  description: Joi.string().optional(),
  location: Joi.string().optional(),
  scheduled_by: Joi.string()
    .guid({ version: 'uuidv4' })
    .optional(),
  course_code: Joi.string().optional()
});
