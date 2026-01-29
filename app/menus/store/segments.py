import json
from app.client.store.segments import get_segments
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special
from app.service.auth import AuthInstance
from app.menus.package import show_package_details

WIDTH = 55

def show_store_segments_menu(is_enterprise: bool = False):
    in_store_segments_menu = True
    while in_store_segments_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print(f"{Colors.GREY}Fetching store segments...{Colors.RESET}")
        segments_res = get_segments(api_key, tokens, is_enterprise)
        if not segments_res:
            print(f"{Colors.YELLOW}No segments found.{Colors.RESET}")
            in_store_segments_menu = False
            continue
        
        segments = segments_res.get("data", {}).get("store_segments", [])
        
        clear_screen()
        
        print(section_header("STORE SEGMENTS", WIDTH))
        
        packages = {}
        for i, segment in enumerate(segments):
            name = segment.get("title", "N/A")
            banners = segment.get("banners", [])
            
            letter = chr(65 + i)  # Convert 0 -> A, 1 -> B, etc.
            print(box_line(WIDTH))
            print(f"  {Colors.CYAN}{letter}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}Banner: {name}{Colors.RESET}")
            print(box_line(WIDTH))
            
            for j, banner in enumerate(banners):
                discounted_price = banner.get("discounted_price", "N/A")
                title = banner.get("title", "N/A")
                validity = banner.get("validity", "N/A")
                family_name = banner.get("family_name", "N/A")
                
                action_param = banner.get("action_param", "")
                action_type = banner.get("action_type", "")
                
                packages[f"{letter.lower()}{j + 1}"] = {
                    "action_param": action_param,
                    "action_type": action_type
                }
                
                print(f"    {Colors.YELLOW}{letter}{j + 1}{Colors.DARK_GREY}.{Colors.RESET} {Colors.LIGHT_GREY}{family_name} - {title}{Colors.RESET}")
                print(f"       {Colors.GREY}Price:{Colors.RESET} {Colors.YELLOW}Rp{discounted_price}{Colors.RESET}")
                print(f"       {Colors.GREY}Validity: {validity}{Colors.RESET}")
                print(box_line(WIDTH))
            
        print(menu_item_special("00", "Back to Main Menu"))
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Enter choice (e.g., A1, B2):{Colors.RESET} ")
        if choice == "00":
            in_store_segments_menu = False
            continue
        
        selected_pkg = packages.get(choice.lower())
        if not selected_pkg:
            print(f"{Colors.YELLOW}Invalid choice.{Colors.RESET}")
            pause()
            continue
        
        action_param = selected_pkg["action_param"]
        action_type = selected_pkg["action_type"]
        
        if action_type == "PDP":
            _ = show_package_details(
                api_key,
                tokens,
                action_param,
                is_enterprise
            )
        else:
            print(section_header("UNHANDLED ACTION", WIDTH))
            print(f"  {Colors.GREY}Action type: {action_type}{Colors.RESET}")
            print(f"  {Colors.GREY}Param: {action_param}{Colors.RESET}")
            pause()
