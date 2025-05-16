from app.services.add_notification_service import add_course_notification, add_one_recipient_notification
from app.services.get_notifications_service import get_notifications
from app.services.get_notification_details_service import get_notification_details
from app.services.get_admin_notifications_service import get_admin_notifications
from app.services.get_admin_notification_details_service import get_admin_notification_details

async def handle_message(payload: dict):
    action = payload.get("action")
    data = payload.get("payload")

    if action == "addCourseNotification":
        return await add_course_notification(data)
    elif action == "addOneRecipientNotification":
        return await add_one_recipient_notification(data)
    elif action == "getNotifications":
        return await get_notifications(data)
    elif action == "getNotificationDetails":
        return await get_notification_details(data)
    elif action == "getAdminNotifications":
        return await get_admin_notifications(data)
    elif action == "getAdminNotificationDetails":
        return await get_admin_notification_details(data)
    else:
        print(f"⚠️ Unknown action: {action}")
        return {"error": f"Unknown action {action}"}