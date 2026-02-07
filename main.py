from dotenv import load_dotenv

from app.service.git import check_for_updates
load_dotenv()

import sys, json
from datetime import datetime
from app.menus.util import clear_screen, pause
from app.menus.colors import (
    Colors, section_header, box_line, menu_item, menu_item_special, 
    info_line, grey, white, cyan, yellow
)
from app.client.engsel import (
    get_balance,
    get_tiering_info,
)
from app.client.famplan import validate_msisdn
from app.menus.payment import show_transaction_history
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.service.sentry import enter_sentry_mode
from app.menus.purchase import purchase_by_family
from app.menus.famplan import show_family_info
from app.menus.circle import show_circle_info
from app.menus.notification import show_notification_menu
from app.menus.store.segments import show_store_segments_menu
from app.menus.store.search import show_family_list_menu, show_store_packages_menu
from app.menus.store.redemables import show_redeemables_menu
from app.menus.catalog_export import show_catalog_export_menu
from app.client.registration import dukcapil

WIDTH = 55

def show_main_menu(profile):
    clear_screen()
    
    # User Profile Section
    print(section_header("USER PROFILE", WIDTH))
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
    print(info_line("Nomor", profile['number']))
    print(info_line("Type", profile['subscription_type']))
    print(info_line("Pulsa", f"Rp {profile['balance']}"))
    print(info_line("Aktif s/d", expired_at_dt))
    print(info_line("Info", profile['point_info'].replace("Points:", "").replace("| Tier:", "Tier:").strip()))
    print(box_line(WIDTH))
    
    # Main Menu Section
    print(section_header("MAIN MENU", WIDTH))
    print(menu_item("1", "Login/Ganti akun"))
    print(menu_item("2", "Lihat Paket Saya"))
    print(menu_item("3", "Beli Paket HOT", highlight=True))
    print(menu_item("4", "Beli Paket HOT-2", highlight=True))
    print(menu_item("5", "Beli Paket Berdasarkan Option Code"))
    print(menu_item("6", "Beli Paket Berdasarkan Family Code"))
    print(menu_item("7", "Beli Semua Paket di Family Code (loop)"))
    print(menu_item("8", "Riwayat Transaksi"))
    print(box_line(WIDTH, '─'))
    print(menu_item_special("N", "Notifikasi"))
    print(menu_item_special("O", "Opsi Selanjutnya"))
    print(menu_item_special("00", "Bookmark Paket"))
    print(menu_item_special("99", "Tutup Aplikasi"))
    print(box_line(WIDTH))

def show_second_menu(profile):
    """Menu kedua dengan fitur-fitur tambahan"""
    from app.menus.famplan import show_family_info
    from app.menus.circle import show_circle_info
    from app.menus.store.segments import show_store_segments_menu
    from app.menus.store.search import show_family_list_menu, show_store_packages_menu
    from app.menus.store.redemables import show_redeemables_menu
    from app.client.registration import dukcapil
    from app.client.famplan import validate_msisdn
    from app.menus.purchase import multi_famcode_purchase
    from app.menus.special_offers import show_special_offers_menu
    
    while True:
        clear_screen()
        expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
        
        # User Profile Section (compact)
        print(section_header("USER PROFILE", WIDTH))
        print(info_line("Nomor", profile['number']))
        print(info_line("Pulsa", f"Rp {profile['balance']} | Aktif s/d: {expired_at_dt}"))
        print(box_line(WIDTH))
        
        # Menu Kedua Section
        print(section_header("MENU KEDUA", WIDTH))
        print(menu_item("1", "Multi-FamCode Purchase"))
        print(menu_item("2", "Special Offers", highlight=True))
        print(menu_item("3", "Catalog Tools"))
        print(box_line(WIDTH, '─'))
        
        # Fitur Lainnya Section
        print(section_header("FITUR LAINNYA", WIDTH))
        print(menu_item_special("C", "Family Plan/Akrab Organizer"))
        print(menu_item_special("D", "Circle"))
        print(menu_item_special("E", "Store Segments"))
        print(menu_item_special("F", "Store Family List"))
        print(menu_item_special("G", "Store Packages"))
        print(menu_item_special("H", "Redemables"))
        print(menu_item_special("I", "Register"))
        print(menu_item_special("J", "Validate msisdn"))
        print(box_line(WIDTH, '─'))
        print(menu_item_special("B", "Kembali ke Menu Utama"))
        print(menu_item_special("99", "Tutup Aplikasi"))
        print(box_line(WIDTH))
        
        choice = input("Pilih menu: ")
        
        if choice == "1":
            print(section_header("MULTI-FAMCODE PURCHASE", 55))
            print(f"  {Colors.GREY}Masukkan family codes (pisahkan dengan koma, max 20){Colors.RESET}")
            print(f"  {Colors.DIM_GREY}Contoh: FAM001,FAM002,FAM003{Colors.RESET}")
            print(box_line(55))
            famcodes_input = input(f"  {Colors.GREY}Family codes:{Colors.RESET} ").strip()
            
            if famcodes_input == "" or famcodes_input == "99":
                continue
            
            # Parse famcodes
            famcodes = [fc.strip() for fc in famcodes_input.split(",") if fc.strip()]
            
            if len(famcodes) == 0:
                print(f"  {Colors.YELLOW}Tidak ada famcode yang valid!{Colors.RESET}")
                pause()
                continue
            
            if len(famcodes) > 20:
                print(f"  {Colors.YELLOW}Terlalu banyak famcode ({len(famcodes)}). Max 20!{Colors.RESET}")
                pause()
                continue
            
            print(box_line(55))
            print(f"  {Colors.CYAN}{len(famcodes)} famcode akan diproses:{Colors.RESET}")
            for i, fc in enumerate(famcodes):
                print(f"  {Colors.WHITE}{i+1}. {fc}{Colors.RESET}")
            print(box_line(55))
            
            confirm = input(f"  {Colors.GREY}Lanjutkan? (y/n):{Colors.RESET} ").lower()
            if confirm != "y":
                continue

            start_from_option = input(f"  {Colors.GREY}Start purchasing from option number (default 1):{Colors.RESET} ")
            try:
                start_from_option = int(start_from_option)
            except ValueError:
                start_from_option = 1

            use_decoy = input(f"  {Colors.GREY}Use decoy package? (y/n):{Colors.RESET} ").lower() == 'y'
            pause_on_success = input(f"  {Colors.GREY}Pause on each successful purchase? (y/n):{Colors.RESET} ").lower() == 'y'
            delay_seconds = input(f"  {Colors.GREY}Delay seconds between purchases (0 for no delay):{Colors.RESET} ")
            try:
                delay_seconds = int(delay_seconds)
            except ValueError:
                delay_seconds = 0
            
            multi_famcode_purchase(
                famcodes,
                use_decoy,
                pause_on_success,
                delay_seconds,
                start_from_option
            )
            pause()
        elif choice == "2":
            show_special_offers_menu()
        elif choice == "3":
            show_catalog_export_menu(profile)
        elif choice.lower() == "c":
            show_family_info(AuthInstance.api_key, AuthInstance.get_active_tokens())
        elif choice.lower() == "d":
            show_circle_info(AuthInstance.api_key, AuthInstance.get_active_tokens())
        elif choice.lower() == "e":
            input_e = input("Is enterprise store? (y/n): ").lower()
            is_enterprise = input_e == 'y'
            show_store_segments_menu(is_enterprise)
        elif choice.lower() == "f":
            input_f = input("Is enterprise? (y/n): ").lower()
            is_enterprise = input_f == 'y'
            show_family_list_menu(profile['subscription_type'], is_enterprise)
        elif choice.lower() == "g":
            input_g = input("Is enterprise? (y/n): ").lower()
            is_enterprise = input_g == 'y'
            show_store_packages_menu(profile['subscription_type'], is_enterprise)
        elif choice.lower() == "h":
            input_h = input("Is enterprise? (y/n): ").lower()
            is_enterprise = input_h == 'y'
            show_redeemables_menu(is_enterprise)
        elif choice.lower() == "i":
            # REGISTER
            print(section_header("REGISTER (DUKCAPIL)", 55))
            msisdn = input(f"  {Colors.GREY}Enter msisdn (628xxxx):{Colors.RESET} ")
            nik = input(f"  {Colors.GREY}Enter NIK:{Colors.RESET} ")
            kk = input(f"  {Colors.GREY}Enter KK:{Colors.RESET} ")
            print(box_line(55))
            print(f"  {Colors.CYAN}Processing registration...{Colors.RESET}")
            
            res = dukcapil(AuthInstance.api_key, msisdn, kk, nik)
            
            print(box_line(55))
            if res.get("status") == "SUCCESS": # Adjust based on actual success response structure if known, usually check status
                 print(f"  {Colors.GREEN}Registration Request Sent!{Colors.RESET}")
            else:
                 print(f"  {Colors.YELLOW}Request Failed/Check Response{Colors.RESET}")
            
            print(f"  {Colors.GREY}Response:{Colors.RESET}")
            print(json.dumps(res, indent=2)) # Keeping JSON dump for details but styled context
            print(box_line(55))
            pause()
        elif choice.lower() == "j":
            # VALIDATE MSISDN
            print(section_header("VALIDATE MSISDN", 55))
            msisdn = input(f"  {Colors.GREY}Enter msisdn to validate (628xxxx):{Colors.RESET} ")
            print(box_line(55))
            print(f"  {Colors.CYAN}Validating...{Colors.RESET}")
            
            res = validate_msisdn(AuthInstance.api_key, AuthInstance.get_active_tokens(), msisdn)
            
            print(box_line(55))
            print(f"  {Colors.GREY}Validation Result:{Colors.RESET}")
            print(json.dumps(res, indent=2))
            print(box_line(55))
            pause()
        elif choice.lower() == "b":
            return  # Kembali ke menu utama
        elif choice == "99":
            print("Exiting the application.")
            sys.exit(0)
        else:
            print("Pilihan tidak valid.")
            pause()

show_menu = True
def main():
    
    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
            balance_remaining = balance.get("remaining")
            balance_expired_at = balance.get("expired_at")
            
            point_info = "Points: N/A | Tier: N/A"
            
            if active_user["subscription_type"] == "PREPAID":
                tiering_data = get_tiering_info(AuthInstance.api_key, active_user["tokens"])
                tier = tiering_data.get("tier", 0)
                current_point = tiering_data.get("current_point", 0)
                point_info = f"Points: {current_point} | Tier: {tier}"
            
            profile = {
                "number": active_user["number"],
                "subscriber_id": active_user["subscriber_id"],
                "subscription_type": active_user["subscription_type"],
                "balance": balance_remaining,
                "balance_expired_at": balance_expired_at,
                "point_info": point_info
            }

            show_main_menu(profile)

            choice = input("Pilih menu: ")
            # Testing shortcuts
            if choice.lower() == "t":
                pause()
            elif choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                else:
                    print("No user selected or failed to load user.")
                continue
            elif choice == "2":
                fetch_my_packages()
                continue
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                print(section_header("PURCHASE BY OPTION CODE", 55))
                option_code = input(f"  {Colors.GREY}Enter option code (or '99' to cancel):{Colors.RESET} ")
                if option_code == "99":
                    continue
                show_package_details(
                    AuthInstance.api_key,
                    AuthInstance.get_active_tokens(),
                    option_code,
                    False
                )
            elif choice == "6":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "7":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue

                start_from_option = input("Start purchasing from option number (default 1): ")
                try:
                    start_from_option = int(start_from_option)
                except ValueError:
                    start_from_option = 1

                use_decoy = input("Use decoy package? (y/n): ").lower() == 'y'
                pause_on_success = input("Pause on each successful purchase? (y/n): ").lower() == 'y'
                delay_seconds = input("Delay seconds between purchases (0 for no delay): ")
                try:
                    delay_seconds = int(delay_seconds)
                except ValueError:
                    delay_seconds = 0
                purchase_by_family(
                    family_code,
                    use_decoy,
                    pause_on_success,
                    delay_seconds,
                    start_from_option
                )
            elif choice == "8":
                show_transaction_history(AuthInstance.api_key, active_user["tokens"])
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice.lower() == "n":
                show_notification_menu()
            elif choice == "s":
                enter_sentry_mode()
            elif choice.lower() == "o":
                show_second_menu(profile)
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
            else:
                print("No user selected or failed to load user.")

if __name__ == "__main__":
    try:
        print("Checking for updates...")
        need_update = check_for_updates()
        if need_update:
            pause()

        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
