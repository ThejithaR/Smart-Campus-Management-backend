// attendanceRoutes.js
import express from "express";
const chatbotRouter = express.Router();

// define routes
chatbotRouter.get("/", (req, res) => {
  res.send("Chatbot Home");
});

export default chatbotRouter;   // <-- IMPORTANT
