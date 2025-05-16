import express from 'express';
import { getUser, updateProfile, signUp, signIn} from '../controllers/userProfileController.js';

const userProfileRouter = express.Router();

// User sign-up
userProfileRouter.post('/sign-up', signUp);
// User sign-in
userProfileRouter.post('/sign-in', signIn);
// Route to get user profile
userProfileRouter.get('/get-user', getUser);
// Route to update user profile
userProfileRouter.post('/update-profile', updateProfile);

export default userProfileRouter;