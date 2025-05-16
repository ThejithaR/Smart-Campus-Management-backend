#from app.db import supabase
from app.supabase.supabaseConfig import supabase

async def get_admin_notification_details(data: dict):
    notification_id = data.get("notificationId")
    print(f"📥 Retrieving details for admin notification: {notification_id}")

    if not notification_id:
        return {"status": "error", "message": "Notification ID is required"}

    try:
        # Query the database for the specific notification
        response = supabase.table("Notifications").select("*").eq("notification_id", notification_id).execute()

        # if response.error:
        #     print(f"❌ Error fetching admin notification details: {response.error}")
        #     return {"status": "error", "message": "Failed to fetch admin notification details"}

        notification = response.data[0]
        print(f"✅ Admin notification details retrieved: {notification}")

        return {"status": "success", "notification": notification}
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return {"status": "error", "message": str(e)}