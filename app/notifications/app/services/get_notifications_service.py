#from app.db import supabase
from app.supabase.supabaseConfig import supabase

async def get_notifications(data: dict):
    user_id = data.get("userId")
    print(f"📥 Retrieving notifications for user: {user_id}")

    if not user_id:
        return {"status": "error", "message": "User ID is required"}

    try:
        # Fetch notifications for the user
        response = supabase.table("Notifications").select("*").eq("recipient_id", user_id).execute()

        print(f"Response: {response}")

        # if response.error:
        #     print(f"❌ Error fetching notifications: {response.error}")
        #     return {"status": "error", "message": "Failed to fetch notifications"}
        if not response.data:
            return {"status": "error", "message": "No notifications found for this user"}

        notifications = response.data
        print(f"✅ Notifications retrieved: {notifications}")

        return {"status": "success", "notifications": notifications}
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return {"status": "error", "message": "An error occurred while fetching notifications"}