from app.client.store.search import get_family_list, get_store_packages
from app.menus.package import get_packages_by_family, show_package_details
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special
from app.service.auth import AuthInstance

WIDTH = 55

def show_family_list_menu(
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    in_family_list_menu = True
    while in_family_list_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print(f"{Colors.GREY}Fetching family list...{Colors.RESET}")
        family_list_res = get_family_list(api_key, tokens, subs_type, is_enterprise)
        if not family_list_res:
            print(f"{Colors.YELLOW}No family list found.{Colors.RESET}")
            in_family_list_menu = False
            continue
        
        family_list = family_list_res.get("data", {}).get("results", [])
        
        clear_screen()
        
        print(section_header("FAMILY LIST", WIDTH))
        
        for i, family in enumerate(family_list):
            family_name = family.get("label", "N/A")
            family_code = family.get("id", "N/A")
            
            print(f"  {Colors.CYAN}{i + 1}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{family_name}{Colors.RESET}")
            print(f"     {Colors.GREY}Family code: {family_code}{Colors.RESET}")
            print(box_line(WIDTH))
        
        print(menu_item_special("00", "Back to Main Menu"))
        print(f"  {Colors.GREY}Input number to view packages in that family.{Colors.RESET}")
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Enter your choice:{Colors.RESET} ")
        if choice == "00":
            in_family_list_menu = False
        
        if choice.isdigit() and int(choice) > 0 and int(choice) <= len(family_list):
            selected_family = family_list[int(choice) - 1]
            family_code = selected_family.get("id", "")
            family_name = selected_family.get("label", "N/A")
            
            print(f"{Colors.GREY}Fetching packages for: {family_name}...{Colors.RESET}")
            get_packages_by_family(family_code)
    
    pause()

def show_store_packages_menu(
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    in_store_packages_menu = True
    while in_store_packages_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print(f"{Colors.GREY}Fetching store packages...{Colors.RESET}")
        store_packages_res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
        if not store_packages_res:
            print(f"{Colors.YELLOW}No store packages found.{Colors.RESET}")
            in_store_packages_menu = False
            continue
        
        store_packages = store_packages_res.get("data", {}).get("results_price_only", [])
        
        clear_screen()
        
        print(section_header("STORE PACKAGES", WIDTH))
        
        packages = {}
        for i, package in enumerate(store_packages):
            title = package.get("title", "N/A")
            
            
            original_price = package.get("original_price", 0)
            discounted_price = package.get("discounted_price", 0)
            
            price = original_price
            if discounted_price > 0:
                price = discounted_price
            
            validity = package.get("validity", "N/A")
            family_name = package.get("family_name", "N/A")
            
            action_type = package.get("action_type", "")
            action_param = package.get("action_param", "")
            
            packages[f"{i + 1}"] = {
                "action_type": action_type,
                "action_param": action_param
            }
            
            print(f"  {Colors.CYAN}{i + 1}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{title}{Colors.RESET}")
            print(f"     {Colors.GREY}Family: {family_name}{Colors.RESET}")
            print(f"     {Colors.GREY}Price:{Colors.RESET} {Colors.YELLOW}Rp{price}{Colors.RESET}")
            print(f"     {Colors.GREY}Validity: {validity}{Colors.RESET}")
            print(box_line(WIDTH))
        
        print(menu_item_special("00", "Back to Main Menu"))
        print(f"  {Colors.GREY}Input number to view package details.{Colors.RESET}")
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Enter your choice:{Colors.RESET} ")
        if choice == "00":
            in_store_packages_menu = False
        elif choice in packages:
            selected_package = packages[choice]
            
            action_type = selected_package["action_type"]
            action_param = selected_package["action_param"]
            
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
        else:
            print(f"{Colors.YELLOW}Invalid choice.{Colors.RESET}")
            pause()