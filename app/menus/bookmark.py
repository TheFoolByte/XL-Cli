from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item
from app.service.bookmark import BookmarkInstance
from app.client.engsel import get_family

def show_bookmark_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print(section_header("BOOKMARK PAKET", 55))
        bookmarks = BookmarkInstance.get_bookmarks()
        if not bookmarks or len(bookmarks) == 0:
            print(f"  {Colors.GREY}Tidak ada bookmark tersimpan.{Colors.RESET}")
            pause()
            return None
        
        for idx, bm in enumerate(bookmarks):
            print(menu_item(str(idx + 1), f"{bm['family_name']} - {bm['variant_name']} - {bm['option_name']}"))
        
        print(box_line(55))
        print(f"  {Colors.SOFT_GREEN}00{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}Kembali ke menu utama{Colors.RESET}")
        print(f"  {Colors.ORANGE}000{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}Hapus Bookmark{Colors.RESET}")
        print(box_line(55))
        choice = input(f"{Colors.GREY}Pilih bookmark: {Colors.RESET}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        elif choice == "000":
            del_choice = input("Masukan nomor bookmark yang ingin dihapus: ")
            if del_choice.isdigit() and 1 <= int(del_choice) <= len(bookmarks):
                del_bm = bookmarks[int(del_choice) - 1]
                BookmarkInstance.remove_bookmark(
                    del_bm["family_code"],
                    del_bm["is_enterprise"],
                    del_bm["variant_name"],
                    del_bm["order"],
                )
            else:
                print("Input tidak valid. Silahkan coba lagi.")
                pause()
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(bookmarks):
            selected_bm = bookmarks[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print("Gagal mengambil data family.")
                pause()
                continue
            
            package_variants = family_data["package_variants"]
            option_code = None
            for variant in package_variants:
                if variant["name"] == selected_bm["variant_name"]:
                    selected_variant = variant
                    
                    package_options = selected_variant["package_options"]
                    for option in package_options:
                        if option["order"] == selected_bm["order"]:
                            selected_option = option
                            option_code = selected_option["package_option_code"]
                            break
            
            if option_code:
                print(f"{option_code}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue