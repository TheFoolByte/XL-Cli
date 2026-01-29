import json

from app.client.engsel import get_family, get_package_details
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, format_quota_byte, pause, display_html
from app.menus.colors import Colors, section_header, box_line, menu_item, info_line, menu_item_special
from app.client.purchase.ewallet import show_multipayment
from app.client.purchase.qris import show_qris_payment
from app.client.purchase.balance import settlement_balance
from app.type_dict import PaymentItem

WIDTH = 55

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print(section_header("PAKET HOT", WIDTH))
        
        hot_packages = []
        
        with open("hot_data/hot.json", "r", encoding="utf-8") as f:
            hot_packages = json.load(f)

        for idx, p in enumerate(hot_packages):
            print(menu_item(str(idx + 1), f"{p['family_name']} - {p['variant_name']} - {p['option_name']}"))
        
        print(box_line(WIDTH))
        print(f"  {Colors.SOFT_YELLOW}00{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}Kembali ke menu utama{Colors.RESET}")
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Pilih paket: {Colors.RESET}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
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
                print(f"{Colors.DIM_GREY}Found Option Code: {option_code}{Colors.RESET}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            else:
                print(f"  {Colors.RED}Gagal menemukan varian/opsi paket di family ini.{Colors.RESET}")
                print(f"  Expected: {selected_bm['variant_name']} - {selected_bm['order']}")
                pause()
            
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue

def show_hot_menu2():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        main_package_detail = {}
        print(section_header("PAKET HOT 2", WIDTH))
        
        hot_packages = []
        
        with open("hot_data/hot2.json", "r", encoding="utf-8") as f:
            hot_packages = json.load(f)

        for idx, p in enumerate(hot_packages):
            print(menu_item(str(idx + 1), f"{p['name']} - {Colors.YELLOW}Rp {p['price']}{Colors.RESET}"))
        
        print(box_line(WIDTH))
        print(f"  {Colors.SOFT_YELLOW}00{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}Kembali ke menu utama{Colors.RESET}")
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Pilih paket:{Colors.RESET} ")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if len(packages) == 0:
                print("Paket tidak tersedia.")
                pause()
                continue
            
            payment_items = []
            for package in packages:
                package_detail = get_package_details(
                    api_key,
                    tokens,
                    package["family_code"],
                    package["variant_code"],
                    package["order"],
                    package["is_enterprise"],
                    package["migration_type"],
                )
                
                if package == packages[0]:
                    main_package_detail = package_detail
                
                # Force failed when one of the package detail is None
                if not package_detail:
                    print(f"Gagal mengambil detail paket untuk {package['family_code']}.")
                    return None
                
                payment_items.append(
                    PaymentItem(
                        item_code=package_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=package_detail["package_option"]["price"],
                        item_name=package_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=package_detail["token_confirmation"],
                    )
                )
            
            clear_screen()
            print("=" * WIDTH)
            print(f"Name: {selected_package['name']}")
            print(f"Price: {selected_package['price']}")
            print(f"Detail: {selected_package['detail']}")
            print("=" * WIDTH)
            print("Main Package Details:".center(WIDTH))
            print("-" * WIDTH)
            # Show package 0 details
            
            price = main_package_detail["package_option"]["price"]
            detail = display_html(main_package_detail["package_option"]["tnc"])
            validity = main_package_detail["package_option"]["validity"]

            option_name = main_package_detail.get("package_option", {}).get("name","") #Vidio
            family_name = main_package_detail.get("package_family", {}).get("name","") #Unlimited Turbo
            variant_name = main_package_detail.get("package_detail_variant", "").get("name","") #For Xtra Combo
            option_name = main_package_detail.get("package_option", {}).get("name","") #Vidio
            
            title = f"{family_name} - {variant_name} - {option_name}".strip()
            
            family_code = main_package_detail.get("package_family", {}).get("package_family_code","")
            parent_code = main_package_detail.get("package_addon", {}).get("parent_code","")
            if parent_code == "":
                parent_code = "N/A"
            
            payment_for = main_package_detail["package_family"]["payment_for"]
                
            print(info_line("Nama", title))
            print(info_line("Harga", f"Rp {price}"))
            print(info_line("Payment For", payment_for))
            print(info_line("Masa Aktif", validity))
            print(info_line("Point", main_package_detail['package_option']['point']))
            print(info_line("Plan Type", main_package_detail['package_family']['plan_type']))
            print(box_line(WIDTH))
            print(info_line("Family Code", family_code))
            print(info_line("Parent Code", parent_code))
            print(box_line(WIDTH))
            benefits = main_package_detail["package_option"]["benefits"]
            if benefits and isinstance(benefits, list):
                print("Benefits:")
                for benefit in benefits:
                    print("-" * WIDTH)
                    print(f" Name: {benefit['name']}")
                    print(f"  Item id: {benefit['item_id']}")
                    data_type = benefit['data_type']
                    if data_type == "VOICE" and benefit['total'] > 0:
                        print(f"  Total: {benefit['total']/60} menit")
                    elif data_type == "TEXT" and benefit['total'] > 0:
                        print(f"  Total: {benefit['total']} SMS")
                    elif data_type == "DATA" and benefit['total'] > 0:
                        if benefit['total'] > 0:
                            quota = int(benefit['total'])
                            quota_formatted = format_quota_byte(quota)
                            print(f"  Total: {quota_formatted} ({data_type})")
                    elif data_type not in ["DATA", "VOICE", "TEXT"]:
                        print(f"  Total: {benefit['total']} ({data_type})")
                    
                    if benefit["is_unlimited"]:
                        print("  Unlimited: Yes")

            print("-" * WIDTH)
            print(f"SnK MyXL:\n{detail}")
            print("-" * WIDTH)
                
            print("=" * WIDTH)
            
            payment_for = selected_package.get("payment_for", "BUY_PACKAGE")
            ask_overwrite = selected_package.get("ask_overwrite", False)
            overwrite_amount = selected_package.get("overwrite_amount", -1)
            token_confirmation_idx = selected_package.get("token_confirmation_idx", 0)
            amount_idx = selected_package.get("amount_idx", -1)

            in_payment_menu = True
            while in_payment_menu:
                print(section_header("PILIH METODE PEMBELIAN", WIDTH))
                print(menu_item("1", "Balance"))
                print(menu_item("2", "E-Wallet"))
                print(menu_item("3", "QRIS"))
                print(box_line(WIDTH))
                print(menu_item_special("00", "Kembali ke menu sebelumnya"))
                print(box_line(WIDTH))
                
                input_method = input(f"{Colors.GREY}Pilih metode (nomor): {Colors.RESET}")
                if input_method == "1":
                    if overwrite_amount == -1:
                        print(f"  {Colors.YELLOW}Pastikan sisa balance KURANG DARI Rp{payment_items[-1]['item_price']}!!!{Colors.RESET}")
                        balance_answer = input(f"  {Colors.GREY}Apakah anda yakin ingin melanjutkan pembelian? (y/n):{Colors.RESET} ")
                        if balance_answer.lower() != "y":
                            print(f"  {Colors.GREY}Pembelian dibatalkan oleh user.{Colors.RESET}")
                            pause()
                            in_payment_menu = False
                            continue

                    settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount=overwrite_amount,
                        token_confirmation_idx=token_confirmation_idx,
                        amount_idx=amount_idx,
                    )
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "2":
                    show_multipayment(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount,
                        token_confirmation_idx,
                        amount_idx,
                    )
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "3":
                    show_qris_payment(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount,
                        token_confirmation_idx,
                        amount_idx,
                    )

                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "00":
                    in_payment_menu = False
                    continue
                else:
                    print("Metode tidak valid. Silahkan coba lagi.")
                    pause()
                    continue
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue
