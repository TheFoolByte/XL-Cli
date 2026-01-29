from app.client.store.redeemables import get_redeemables
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special
from app.menus.package import show_package_details, get_packages_by_family

from datetime import datetime

WIDTH = 55

def show_redeemables_menu(is_enterprise: bool = False):
    in_redeemables_menu = True
    while in_redeemables_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print(f"{Colors.GREY}Fetching redeemables...{Colors.RESET}")
        redeemables_res = get_redeemables(api_key, tokens, is_enterprise)
        if not redeemables_res:
            print(f"{Colors.YELLOW}No redeemables found.{Colors.RESET}")
            in_redeemables_menu = False
            continue
        
        categories = redeemables_res.get("data", {}).get("categories", [])
        
        clear_screen()
        
        print(section_header("REDEEMABLES", WIDTH))
        
        packages = {}
        for i, category in enumerate(categories):
            category_name = category.get("category_name", "N/A")
            category_code = category.get("category_code", "N/A")
            redemables = category.get("redeemables", [])
            
            letter = chr(65 + i)
            print(box_line(WIDTH))
            print(f"  {Colors.CYAN}{letter}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}Category: {category_name}{Colors.RESET}")
            print(f"     {Colors.GREY}Code: {category_code}{Colors.RESET}")
            print(box_line(WIDTH))
            
            if len(redemables) == 0:
                print(f"    {Colors.GREY}No redeemables in this category.{Colors.RESET}")
                continue
            
            for j, redemable in enumerate(redemables):
                name = redemable.get("name", "N/A")
                valid_until = redemable.get("valid_until", 0)
                valid_until_date = datetime.strftime(
                    datetime.fromtimestamp(valid_until), "%Y-%m-%d"
                )
                
                action_param = redemable.get("action_param", "")
                action_type = redemable.get("action_type", "")
                
                packages[f"{letter.lower()}{j + 1}"] = {
                    "action_param": action_param,
                    "action_type": action_type
                }
                
                print(f"    {Colors.YELLOW}{letter}{j + 1}{Colors.DARK_GREY}.{Colors.RESET} {Colors.LIGHT_GREY}{name}{Colors.RESET}")
                print(f"       {Colors.GREY}Valid Until: {valid_until_date}{Colors.RESET}")
                print(f"       {Colors.GREY}Action Type: {action_type}{Colors.RESET}")
                print(box_line(WIDTH))
                
        print(menu_item_special("00", "Back"))
        print(f"  {Colors.GREY}Enter choice to view (e.g., A1, B2):{Colors.RESET}")
        print(box_line(WIDTH))
        
        choice = input(f"{Colors.GREY}Choice:{Colors.RESET} ")
        if choice == "00":
            in_redeemables_menu = False
            continue
        selected_pkg = packages.get(choice.lower())
        if not selected_pkg:
            print(f"{Colors.YELLOW}Invalid choice.{Colors.RESET}")
            pause()
            continue
        action_param = selected_pkg["action_param"]
        action_type = selected_pkg["action_type"]
        
        if action_type == "PLP":
            get_packages_by_family(action_param, is_enterprise, "")
        elif action_type == "PDP":
            show_package_details(
                api_key,
                tokens,
                action_param,
                is_enterprise,
            )
        else:
            print(section_header("UNHANDLED ACTION", WIDTH))
            print(f"  {Colors.GREY}Action type: {action_type}{Colors.RESET}")
            print(f"  {Colors.GREY}Param: {action_param}{Colors.RESET}")
            pause()
