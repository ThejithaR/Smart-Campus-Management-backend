#from app.db import supabase
from app.supabase.supabaseConfig import supabase

async def get_admin_notifications(data: dict):
    faculty_member_id = data.get("facultyId")
    print(f"📥 Retrieving notifications sent by faculty: {faculty_member_id}")

    if not faculty_member_id:
        return {"status": "error", "message": "Faculty ID is required"}

    try:
        # Query the database for notifications sent by the admin
        response = supabase.table("Notifications").select("*").eq("sender_id", faculty_member_id).execute()

        # if response.get('error'):
        #     print(f"❌ Error fetching admin notifications: {response.error}")
        #     return {"status": "error", "message": "Failed to fetch admin notifications"}

        if not response.data:
            return {"status": "error", "message": "No notifications found for this faculty member"}

        notifications = response.data
        print(f"✅ Admin notifications retrieved: {notifications}")

        return {"status": "success", "notifications": notifications}
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return {"status": "error", "message": str(e)}