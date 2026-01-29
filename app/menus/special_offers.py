import json

from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item

WIDTH = 55

def show_special_offers_menu():
    """
    Menu Special Offers untuk Menu Kedua.
    File data: hot_data/special_offers.json
    Terpisah dari hot.json sehingga bisa diedit sendiri.
    """
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_menu = True
    while in_menu:
        clear_screen()
        print(section_header("SPECIAL OFFERS", WIDTH))
        
        # Load packages dari file terpisah
        special_packages = []
        try:
            with open("hot_data/special_offers.json", "r", encoding="utf-8") as f:
                special_packages = json.load(f)
        except FileNotFoundError:
            print(f"  {Colors.YELLOW}File special_offers.json tidak ditemukan!{Colors.RESET}")
            print(f"  {Colors.GREY}Buat file di: hot_data/special_offers.json{Colors.RESET}")
            pause()
            return None
        except json.JSONDecodeError:
            print(f"  {Colors.YELLOW}Format JSON tidak valid!{Colors.RESET}")
            pause()
            return None
        
        if len(special_packages) == 0:
            print(f"  {Colors.GREY}Belum ada paket yang ditambahkan.{Colors.RESET}")
            print(f"  {Colors.GREY}Edit file: hot_data/special_offers.json{Colors.RESET}")
            pause()
            return None

        for idx, p in enumerate(special_packages):
            print(menu_item(str(idx + 1), f"{p['family_name']} - {p['variant_name']} - {p['option_name']}"))
        
        print(box_line(WIDTH))
        print(f"  {Colors.SOFT_YELLOW}00{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}Kembali ke menu sebelumnya{Colors.RESET}")
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Pilih paket: {Colors.RESET}")
        
        if choice == "00":
            in_menu = False
            return None
            
        if choice.isdigit() and 1 <= int(choice) <= len(special_packages):
            selected_pkg = special_packages[int(choice) - 1]
            family_code = selected_pkg["family_code"]
            is_enterprise = selected_pkg.get("is_enterprise", False)
            
            # Refresh tokens
            tokens = AuthInstance.get_active_tokens()
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print("❌ Gagal mengambil data family.")
                pause()
                continue
            
            package_variants = family_data["package_variants"]
            option_code = None
            
            for variant in package_variants:
                if variant["name"] == selected_pkg["variant_name"]:
                    selected_variant = variant
                    
                    package_options = selected_variant["package_options"]
                    for option in package_options:
                        if option["order"] == selected_pkg["order"]:
                            option_code = option["package_option_code"]
                            break
            
            if option_code:
                print(f"Option Code: {option_code}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            else:
                print("❌ Paket tidak ditemukan dalam family.")
                pause()
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue
