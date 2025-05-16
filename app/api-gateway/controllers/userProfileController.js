//import { v4 as uuidv4 } from 'uuid';
import {publishMessageWithReply} from "../services/rabbitmqService.js";

const QUEUE_NAME = "user_profiles_queue"; // (define queue name here)
// const QUEUE_NAME_RESPONSE = "user_profiles_response_queue"; // (define queue name here)

export const signUp = async (req, res) => {
  try {
    const { email, password, username } = req.body;

    console.log("SignUp Request:", { email, password, username });

    const response = await publishMessageWithReply(QUEUE_NAME,{
      action: "signUp",
      payload: { email, password, username }
    });

    console.log("SignUp Response:", response);

    res.status(200).json({ success: true, message: "SignUp request sent." , response: response });
  } catch (error) {
    console.error("SignUp Error:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
};

export const signIn = async (req, res) => {
  try {
    const { email, password } = req.body;

    console.log("SignIn Request:", { email, password });

    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "signIn",
      payload: { email, password }
    });

    console.log("SignIn Response:", response);

    res.status(200).json({ success: true, message: "SignIn request sent." , response: response });
  } catch (error) {
    console.error("SignIn Error:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
};

export const getUser = async (req, res) => {
  try {
    const { userId } = req.params;

    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "getUser",
      payload: { userId }
    });

    confirm.log("GetUser Response:", response);

    res.status(200).json({ success: true, message: "GetUser request sent." , response: response });
  } catch (error) {
    console.error("GetUser Error:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
};

export const updateProfile = async (req, res) => {
  try {
    const { userId } = req.params;
    const updates = req.body;

    const response = await publishMessageWithReply(QUEUE_NAME, {
      action: "updateProfile",
      payload: { userId, updates }
    });

    console.log("UpdateProfile Response:", response);

    res.status(200).json({ success: true, message: "UpdateProfile request sent." , response: response });
  } catch (error) {
    console.error("UpdateProfile Error:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
};
