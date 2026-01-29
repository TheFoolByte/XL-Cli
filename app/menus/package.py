import json
import sys

import requests
from app.service.auth import AuthInstance
from app.client.engsel import get_family, get_package, get_addons, get_package_details, send_api_request, unsubscribe
from app.client.ciam import get_auth_code
from app.service.bookmark import BookmarkInstance
from app.client.purchase.redeem import settlement_bounty, settlement_loyalty, bounty_allotment
from app.menus.util import clear_screen, pause, display_html
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special, info_line
from app.client.purchase.qris import show_qris_payment
from app.client.purchase.ewallet import show_multipayment
from app.client.purchase.balance import settlement_balance
from app.type_dict import PaymentItem
from app.menus.purchase import purchase_n_times, purchase_n_times_by_option_code
from app.menus.util import format_quota_byte
from app.service.decoy import DecoyInstance

WIDTH = 55

def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order = -1):
    active_user = AuthInstance.active_user
    subscription_type = active_user.get("subscription_type", "")
    
    clear_screen()
    print(section_header("DETAIL PAKET", WIDTH))
    package = get_package(api_key, tokens, package_option_code)
    # print(f"[SPD-202]:\n{json.dumps(package, indent=1)}")
    if not package:
        print("Failed to load package details.")
        pause()
        return False

    price = package["package_option"]["price"]
    detail = display_html(package["package_option"]["tnc"])
    validity = package["package_option"]["validity"]

    option_name = package.get("package_option", {}).get("name","") #Vidio
    family_name = package.get("package_family", {}).get("name","") #Unlimited Turbo
    variant_name = package.get("package_detail_variant", "").get("name","") #For Xtra Combo
    option_name = package.get("package_option", {}).get("name","") #Vidio
    
    title = f"{family_name} - {variant_name} - {option_name}".strip()
    
    family_code = package.get("package_family", {}).get("package_family_code","")
    parent_code = package.get("package_addon", {}).get("parent_code","")
    if parent_code == "":
        parent_code = "N/A"
    
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"]
    
    payment_items = [
        PaymentItem(
            item_code=package_option_code,
            product_type="",
            item_price=price,
            item_name=f"{variant_name} {option_name}".strip(),
            tax=0,
            token_confirmation=token_confirmation,
        )
    ]
    
    print(box_line(WIDTH))
    print(info_line("Nama", title))
    print(info_line("Harga", f"{Colors.YELLOW}Rp {price}{Colors.RESET}"))
    print(info_line("Payment For", payment_for))
    print(info_line("Masa Aktif", validity))
    print(info_line("Point", package['package_option']['point']))
    print(info_line("Plan Type", package['package_family']['plan_type']))
    print(box_line(WIDTH))
    print(info_line("Family Code", family_code))
    print(info_line("Parent Code", parent_code))
    print(box_line(WIDTH))
    benefits = package["package_option"]["benefits"]
    if benefits and isinstance(benefits, list):
        print("Benefits:")
        for benefit in benefits:
            print("-------------------------------------------------------")
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
                    # It is in byte, make it in GB
                    if quota >= 1_000_000_000:
                        quota_gb = quota / (1024 ** 3)
                        print(f"  Quota: {quota_gb:.2f} GB")
                    elif quota >= 1_000_000:
                        quota_mb = quota / (1024 ** 2)
                        print(f"  Quota: {quota_mb:.2f} MB")
                    elif quota >= 1_000:
                        quota_kb = quota / 1024
                        print(f"  Quota: {quota_kb:.2f} KB")
                    else:
                        print(f"  Total: {quota}")
            elif data_type not in ["DATA", "VOICE", "TEXT"]:
                print(f"  Total: {benefit['total']} ({data_type})")
            
            if benefit["is_unlimited"]:
                print("  Unlimited: Yes")
    print("-------------------------------------------------------")
    addons = get_addons(api_key, tokens, package_option_code)
    

    bonuses = addons.get("bonuses", [])
    
    # Pick 1st bonus if available, need more testing
    # if len(bonuses) > 0:
    #     payment_items.append(
    #         PaymentItem(
    #             item_code=bonuses[0]["package_option_code"],
    #             product_type="",
    #             item_price=0,
    #             item_name=bonuses[0]["name"],
    #             tax=0,
    #             token_confirmation="",
    #         )
    #     )
    
    # Pick all bonuses, need more testing
    # for bonus in bonuses:
    #     payment_items.append(
    #         PaymentItem(
    #             item_code=bonus["package_option_code"],
    #             product_type="",
    #             item_price=0,
    #             item_name=bonus["name"],
    #             tax=0,
    #             token_confirmation="",
    #         )
    #     )

    print(f"{Colors.GREY}Addons:{Colors.RESET}\n{json.dumps(addons, indent=2)}")
    print(box_line(WIDTH))
    print(f"{Colors.GREY}SnK MyXL:{Colors.RESET}\n{detail}")
    print(box_line(WIDTH))
    
    in_package_detail_menu = True
    while in_package_detail_menu:
        print(section_header("OPSI PEMBELIAN", WIDTH))
        print(menu_item("1", "Beli dengan Pulsa"))
        print(menu_item("2", "Beli dengan E-Wallet"))
        print(menu_item("3", "Bayar dengan QRIS"))
        print(menu_item("4", "Pulsa + Decoy"))
        print(menu_item("5", "Pulsa + Decoy V2"))
        print(menu_item("6", "QRIS + Decoy (+1K)"))
        print(menu_item("7", "QRIS + Decoy V2"))
        print(menu_item("8", "Pulsa N kali"))

        # Sometimes payment_for is empty, so we set default to BUY_PACKAGE
        if payment_for == "":
            payment_for = "BUY_PACKAGE"
        
        if payment_for == "REDEEM_VOUCHER":
            print(menu_item_special("B", "Ambil sebagai bonus (jika tersedia)"))
            print(menu_item_special("BA", "Kirim bonus (jika tersedia)"))
            print(menu_item_special("L", "Beli dengan Poin (jika tersedia)"))
        
        if option_order != -1:
            print(menu_item_special("0", "Tambah ke Bookmark"))
        print(menu_item_special("00", "Kembali ke daftar paket"))
        print(box_line(WIDTH))

        choice = input(f"{Colors.GREY}Pilihan: {Colors.RESET}")
        if choice == "00":
            return False
        elif choice == "0" and option_order != -1:
            # Add to bookmark
            success = BookmarkInstance.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code",""),
                family_name=package.get("package_family", {}).get("name",""),
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            if success:
                print("Paket berhasil ditambahkan ke bookmark.")
            else:
                print("Paket sudah ada di bookmark.")
            pause()
            continue
        
        elif choice == '1':
            settlement_balance(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True
            )
            input("Silahkan cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '2':
            show_multipayment(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '3':
            show_qris_payment(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '4':
            # Balance with Decoy            
            decoy = DecoyInstance.get_decoy("balance")
            
            decoy_package_detail = get_package(
                api_key,
                tokens,
                decoy["option_code"],
            )
            
            if not decoy_package_detail:
                print(f"  {Colors.RED}Failed to load decoy package details.{Colors.RESET}")
                pause()
                return False

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )

            overwrite_amount = price + decoy_package_detail["package_option"]["price"]
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                payment_for,
                False,
                overwrite_amount=overwrite_amount,
            )
            
            if res and res.get("status", "") != "SUCCESS":
                error_msg = res.get("message", "Unknown error")
                if "Bizz-err.Amount.Total" in error_msg:
                    error_msg_arr = error_msg.split("=")
                    valid_amount = int(error_msg_arr[1].strip())
                    
                    print(f"Adjusted total amount to: {valid_amount}")
                    res = settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        False,
                        overwrite_amount=valid_amount,
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        print("Purchase successful!")
            else:
                print("Purchase successful!")
            pause()
            return True
        elif choice == '5':
            # Balance with Decoy v2 (use token confirmation from decoy)
            decoy = DecoyInstance.get_decoy("balance")
            
            decoy_package_detail = get_package(
                api_key,
                tokens,
                decoy["option_code"],
            )
            
            if not decoy_package_detail:
                print(f"  {Colors.RED}Failed to load decoy package details.{Colors.RESET}")
                pause()
                return False

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )

            overwrite_amount = price + decoy_package_detail["package_option"]["price"]
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                "🤫",
                False,
                overwrite_amount=overwrite_amount,
                token_confirmation_idx=1
            )
            
            if res and res.get("status", "") != "SUCCESS":
                error_msg = res.get("message", "Unknown error")
                if "Bizz-err.Amount.Total" in error_msg:
                    error_msg_arr = error_msg.split("=")
                    valid_amount = int(error_msg_arr[1].strip())
                    
                    print(f"Adjusted total amount to: {valid_amount}")
                    res = settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        "🤫",
                        False,
                        overwrite_amount=valid_amount,
                        token_confirmation_idx=-1
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        print("Purchase successful!")
            else:
                print("Purchase successful!")
            pause()
            return True
        elif choice == '6':
            # QRIS decoy + Rpx
            decoy = DecoyInstance.get_decoy("qris")
            
            decoy_package_detail = get_package(
                api_key,
                tokens,
                decoy["option_code"],
            )
            
            if not decoy_package_detail:
                print(f"  {Colors.RED}Failed to load decoy package details.{Colors.RESET}")
                pause()
                return False

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )
            
            print("-"*55)
            print(f"Harga Paket Utama: Rp {price}")
            print(f"Harga Paket Decoy: Rp {decoy_package_detail['package_option']['price']}")
            print("Silahkan sesuaikan amount (trial & error, 0 = malformed)")
            print("-"*55)

            show_qris_payment(
                api_key,
                tokens,
                payment_items,
                "SHARE_PACKAGE",
                True,
                token_confirmation_idx=1
            )
            
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '7':
            # QRIS decoy + Rp0
            decoy = DecoyInstance.get_decoy("qris0")
            
            decoy_package_detail = get_package(
                api_key,
                tokens,
                decoy["option_code"],
            )
            
            if not decoy_package_detail:
                print(f"  {Colors.RED}Failed to load decoy package details.{Colors.RESET}")
                pause()
                return False

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )
            
            print("-"*55)
            print(f"Harga Paket Utama: Rp {price}")
            print(f"Harga Paket Decoy: Rp {decoy_package_detail['package_option']['price']}")
            print("Silahkan sesuaikan amount (trial & error, 0 = malformed)")
            print("-"*55)

            show_qris_payment(
                api_key,
                tokens,
                payment_items,
                "SHARE_PACKAGE",
                True,
                token_confirmation_idx=1
            )
            
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '8':
            #Pulsa N kali
            use_decoy_input = input(f"  {Colors.GREY}Use decoy package? (y/n):{Colors.RESET} ").strip().lower()
            use_decoy_for_n_times = use_decoy_input == 'y'
            
            n_times_str = input(f"  {Colors.GREY}Enter number of times to purchase (e.g., 3):{Colors.RESET} ").strip()

            delay_seconds_str = input(f"  {Colors.GREY}Enter delay between purchases in seconds (e.g., 25):{Colors.RESET} ").strip()
            if not delay_seconds_str.isdigit():
                delay_seconds_str = "0"

            try:
                n_times = int(n_times_str)
                if n_times < 1:
                    raise ValueError("Number must be at least 1.")
            except ValueError:
                print(f"  {Colors.YELLOW}Invalid number entered. Please enter a valid integer.{Colors.RESET}")
                pause()
                continue
            purchase_n_times_by_option_code(
                n_times,
                option_code=package_option_code,
                use_decoy=use_decoy_for_n_times,
                delay_seconds=int(delay_seconds_str),
                pause_on_success=False,
                token_confirmation_idx=1
            )
        elif choice.lower() == 'b':
            settlement_bounty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
                item_name=variant_name
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice.lower() == 'ba':
            destination_msisdn = input("Masukkan nomor tujuan bonus (mulai dengan 62): ").strip()
            bounty_allotment(
                api_key=api_key,
                tokens=tokens,
                ts_to_sign=ts_to_sign,
                destination_msisdn=destination_msisdn,
                item_name=option_name,
                item_code=package_option_code,
                token_confirmation=token_confirmation,
            )
            pause()
            return True
        elif choice.lower() == 'l':
            settlement_loyalty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        else:
            print("Purchase cancelled.")
            return False
    pause()
    sys.exit(0)

def get_packages_by_family(
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None
    
    packages = []
    
    data = get_family(
        api_key,
        tokens,
        family_code,
        is_enterprise,
        migration_type
    )
    
    if not data:
        print("Failed to load family data.")
        pause()
        return None
    price_currency = "Rp"
    rc_bonus_type = data["package_family"].get("rc_bonus_type", "")
    if rc_bonus_type == "MYREWARDS":
        price_currency = "Poin"
    
    in_package_menu = True
    while in_package_menu:
        clear_screen()
        # print(f"[GPBF-283]:\n{json.dumps(data, indent=2)}")
        print(section_header("DAFTAR PAKET", WIDTH))
        print(info_line("Family Name", data['package_family']['name']))
        print(info_line("Family Code", family_code))
        print(info_line("Family Type", data['package_family']['package_family_type']))
        print(info_line("Variants", len(data['package_variants'])))
        print(box_line(WIDTH))
        print(f"  {Colors.CYAN}Paket Tersedia{Colors.RESET}")
        print(box_line(WIDTH))
        
        package_variants = data["package_variants"]
        
        option_number = 1
        variant_number = 1
        
        for variant in package_variants:
            variant_name = variant["name"]
            variant_code = variant["package_variant_code"]
            print(f" Variant {variant_number}: {variant_name}")
            print(f" Code: {variant_code}")
            for option in variant["package_options"]:
                option_name = option["name"]
                
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                                
                print(f"   {option_number}. {option_name} - {price_currency} {option['price']}")
                
                option_number += 1
            
            if variant_number < len(package_variants):
                print(box_line(WIDTH))
            variant_number += 1
        print(box_line(WIDTH))

        print(menu_item_special("00", "Kembali ke menu utama"))
        print(box_line(WIDTH))
        pkg_choice = input(f"{Colors.GREY}Pilih paket:{Colors.RESET} ")
        if pkg_choice == "00":
            in_package_menu = False
            return None
        
        if isinstance(pkg_choice, str) == False or not pkg_choice.isdigit():
            print("Input tidak valid. Silakan masukan nomor paket.")
            continue
        
        selected_pkg = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        
        if not selected_pkg:
            print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
            continue
        
        show_package_details(
            api_key,
            tokens,
            selected_pkg["code"],
            is_enterprise,
            option_order=selected_pkg["option_order"],
        )
        
    return packages

def fetch_my_packages():
    in_my_packages_menu = True
    while in_my_packages_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        if not tokens:
            print("No active user tokens found.")
            pause()
            return None
        
        id_token = tokens.get("id_token")
        
        path = "api/v8/packages/quota-details"
        
        payload = {
            "is_enterprise": False,
            "lang": "en",
            "family_member_id": ""
        }
        
        print("Fetching my packages...")
        res = send_api_request(api_key, path, payload, id_token, "POST")
        if res.get("status") != "SUCCESS":
            print("Failed to fetch packages")
            print("Response:", res)
            pause()
            return None
        
        quotas = res["data"]["quotas"]
        
        clear_screen()
        print(section_header("PAKET SAYA", WIDTH))
        my_packages =[]
        num = 1
        for quota in quotas:
            quota_code = quota["quota_code"] # Can be used as option_code
            group_code = quota["group_code"]
            group_name = quota["group_name"]
            quota_name = quota["name"]
            family_code = "N/A"
            
            product_subscription_type = quota.get("product_subscription_type", "")
            product_domain = quota.get("product_domain", "")
            
            benefit_infos = []
            benefits = quota.get("benefits", [])
            if len(benefits) > 0:
                for benefit in benefits:
                    benefit_id = benefit.get("id", "")
                    name = benefit.get("name", "")
                    data_type = benefit.get("data_type", "N/A")
                    benefit_info = "  -----------------------------------------------------\n"
                    benefit_info += f"  ID    : {benefit_id}\n"
                    benefit_info += f"  Name  : {name}\n"
                    benefit_info += f"  Type  : {data_type}\n"
                    

                    remaining = benefit.get("remaining", 0)
                    total = benefit.get("total", 0)

                    if data_type == "DATA":
                        remaining_str = format_quota_byte(remaining)
                        total_str = format_quota_byte(total)
                        
                        benefit_info += f"  Kuota : {remaining_str} / {total_str}"
                    elif data_type == "VOICE":
                        benefit_info += f"  Kuota : {remaining/60:.2f} / {total/60:.2f} menit"
                    elif data_type == "TEXT":
                        benefit_info += f"  Kuota : {remaining} / {total} SMS"
                    else:
                        benefit_info += f"  Kuota : {remaining} / {total}"

                    benefit_infos.append(benefit_info)
                
            
            print(f"fetching package no. {num} details...")
            package_details = get_package(api_key, tokens, quota_code)
            if package_details:
                family_code = package_details["package_family"]["package_family_code"]
            
            print(box_line(WIDTH))
            print(f"  {Colors.CYAN}Package {num}{Colors.RESET}")
            print(f"  {Colors.WHITE}{quota_name}{Colors.RESET}")       
            print(box_line(WIDTH))
            print(f"  {Colors.CYAN}Benefits:{Colors.RESET}")
            if len(benefit_infos) > 0:
                for bi in benefit_infos:
                    # bi already contains some formatting but we can trust it for now or strip colors if needed
                    # ideally we would style bi generation too but let's just print it.
                    # bi has newlines, so just print
                    print(f"{Colors.GREY}{bi}{Colors.RESET}", end="")
                print(box_line(WIDTH))
            print(info_line("Group Name", group_name))
            print(info_line("Quota Code", quota_code))
            print(info_line("Family Code", family_code))
            print(info_line("Group Code", group_code))
            print(box_line(WIDTH))
            
            my_packages.append({
                "number": num,
                "name": quota_name,
                "quota_code": quota_code,
                "product_subscription_type": product_subscription_type,
                "product_domain": product_domain,
            })
            
            num += 1
        
        print(f"  {Colors.GREY}Input package number to view detail.{Colors.RESET}")
        print(f"  {Colors.GREY}Input del <number> to unsubscribe{Colors.RESET}")
        print(menu_item_special("00", "Back to Main Menu"))
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Choice:{Colors.RESET} ")
        if choice == "00":
            in_my_packages_menu = False

        # Handle seletcting package to view detail
        if choice.isdigit() and int(choice) > 0 and int(choice) <= len(my_packages):
            selected_pkg = next((pkg for pkg in my_packages if pkg["number"] == int(choice)), None)
            if not selected_pkg:
                print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
                pause()
                continue
            
            _ = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
        
        elif choice.startswith("del "):
            del_parts = choice.split(" ")
            if len(del_parts) != 2 or not del_parts[1].isdigit():
                print("Invalid input for delete command.")
                pause()
            
            del_number = int(del_parts[1])
            del_pkg = next((pkg for pkg in my_packages if pkg["number"] == del_number), None)
            if not del_pkg:
                print("Package not found for deletion.")
                pause()
            
            confirm = input(f"{Colors.RED}Are you sure you want to unsubscribe from package {del_number}. {del_pkg['name']}? (y/n):{Colors.RESET} ")
            if confirm.lower() == 'y':
                print(f"Unsubscribing from package number {del_pkg['name']}...")
                success = unsubscribe(
                    api_key,
                    tokens,
                    del_pkg["quota_code"],
                    del_pkg["product_subscription_type"],
                    del_pkg["product_domain"]
                )
                if success:
                    print(f"  {Colors.GREEN}Successfully unsubscribed from the package.{Colors.RESET}")
                else:
                    print(f"  {Colors.RED}Failed to unsubscribe from the package.{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}Unsubscribe cancelled.{Colors.RESET}")
            pause()
