from app.menus.util import clear_screen
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special
from app.client.engsel import get_notification_detail, dashboard_segments
from app.service.auth import AuthInstance

WIDTH = 55

def show_notification_menu():
    in_notification_menu = True
    while in_notification_menu:
        clear_screen()
        print(f"{Colors.GREY}Fetching notifications...{Colors.RESET}")
        
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        notifications_res = dashboard_segments(api_key, tokens)
        if not notifications_res:
            print(f"{Colors.YELLOW}No notifications found.{Colors.RESET}")
            return
        
        notifications = notifications_res.get("data", {}).get("notification", {}).get("data", [])
        if not notifications:
            print(f"{Colors.GREY}No notifications available.{Colors.RESET}")
            return
        
        print(section_header("NOTIFICATIONS", WIDTH))
        unread_count = 0
        for idx, notification in enumerate(notifications):
            is_read = notification.get("is_read", False)
            full_message = notification.get("full_message", "")
            brief_message = notification.get("brief_message", "")
            time = notification.get("timestamp", "")
            
            if is_read:
                status = f"{Colors.GREY}READ{Colors.RESET}"
            else:
                status = f"{Colors.YELLOW}UNREAD{Colors.RESET}"
                unread_count += 1

            print(f"  {Colors.CYAN}{idx + 1}{Colors.DARK_GREY}.{Colors.RESET} [{status}] {Colors.WHITE}{brief_message}{Colors.RESET}")
            print(f"     {Colors.GREY}Time: {time}{Colors.RESET}")
            print(f"     {Colors.LIGHT_GREY}{full_message}{Colors.RESET}")
            print(box_line(WIDTH))
        print(f"  {Colors.GREY}Total: {len(notifications)} | Unread: {unread_count}{Colors.RESET}")
        print(box_line(WIDTH))
        print(menu_item("1", "Read All Unread Notifications"))
        print(menu_item_special("00", "Back to Main Menu"))
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Enter your choice:{Colors.RESET} ")
        if choice == "1":
            for notification in notifications:
                if notification.get("is_read", False):
                    continue
                notification_id = notification.get("notification_id")
                detail = get_notification_detail(api_key, tokens, notification_id)
                if detail:
                    print(f"Mark as READ notification ID: {notification_id}")
            input("Press Enter to return to the notification menu...")
        elif choice == "00":
            in_notification_menu = False
        else:
            print("Invalid choice. Please try again.")
