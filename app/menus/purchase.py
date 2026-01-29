import requests, time, os, json
from random import randint
from datetime import datetime
from app.client.engsel import get_family, get_package_details, get_package
from app.menus.util import pause
from app.menus.colors import Colors, section_header, box_line, info_line
from app.service.auth import AuthInstance
from app.service.decoy import DecoyInstance
from app.type_dict import PaymentItem
from app.client.purchase.balance import settlement_balance

# Ensure results folder exists
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

def save_result_to_file(famcode: str, package_info: str, result: dict):
    """Save successful purchase result to results folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RESULTS_DIR}/purchase_{timestamp}_{famcode}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "famcode": famcode,
        "package": package_info,
        "result": result
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Result saved to: {filename}")
    return filename

def multi_famcode_purchase(
    famcodes: list,
    use_decoy: bool = False,
    pause_on_success: bool = True,
    delay_seconds: int = 0,
    start_from_option: int = 1
):
    """
    Purchase all packages from multiple family codes.
    - Max 20 famcodes
    - Asks user to continue after each successful purchase
    - Saves results to 'results' folder
    """
    if len(famcodes) > 20:
        print(f"{Colors.YELLOW}Maksimal 20 famcode yang bisa diproses!{Colors.RESET}")
        pause()
        return False
    
    if len(famcodes) == 0:
        print(f"{Colors.YELLOW}Tidak ada famcode yang diinput!{Colors.RESET}")
        pause()
        return False
    
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    total_famcodes = len(famcodes)
    all_successful_purchases = []
    stopped_by_user = False
    
    print(section_header("MULTI-FAMCODE PURCHASE", 55))
    print(f"  {Colors.GREY}Total famcodes: {Colors.WHITE}{total_famcodes}{Colors.RESET}")
    print(box_line(55))

    if use_decoy:
        # Balance with Decoy - Prompt ONCE
        decoy = DecoyInstance.get_decoy("balance")
        
        decoy_package_detail = get_package(
            api_key,
            tokens,
            decoy["option_code"],
        )
        
        if not decoy_package_detail:
            print(f"  {Colors.YELLOW}Failed to load decoy package details.{Colors.RESET}")
            pause()
            return False
        
        balance_treshold = decoy_package_detail["package_option"]["price"]
        print(f"  {Colors.YELLOW}Pastikan sisa balance KURANG DARI Rp{balance_treshold}!!!{Colors.RESET}")
        balance_answer = input(f"  {Colors.GREY}Apakah anda yakin ingin melanjutkan pembelian? (y/n):{Colors.RESET} ")
        if balance_answer.lower() != "y":
            print(f"  {Colors.GREY}Pembelian dibatalkan oleh user.{Colors.RESET}")
            pause()
            return False

    
    for famcode_idx, family_code in enumerate(famcodes):
        if stopped_by_user:
            break
            
        print(section_header(f"FAMCODE {famcode_idx + 1}/{total_famcodes}", 55))
        print(f"  {Colors.CYAN}Code:{Colors.RESET} {Colors.WHITE}{family_code}{Colors.RESET}")
        print(box_line(55))
        
        # Get family data
        tokens = AuthInstance.get_active_tokens()
        family_data = get_family(api_key, tokens, family_code)
        
        if not family_data:
            print(f"  {Colors.RED}Failed to get family data for: {family_code}{Colors.RESET}")
            continue
        
        family_name = family_data["package_family"]["name"]
        variants = family_data["package_variants"]
        
        print(info_line("Family", family_name))
        
        # Count total packages
        packages_count = sum(len(v["package_options"]) for v in variants)
        print(info_line("Total packages", packages_count))
        print(box_line(55))
        
        purchase_count = 0
        start_buying = False
        if start_from_option <= 1:
            start_buying = True
        
        for variant in variants:
            if stopped_by_user:
                break
                
            variant_name = variant["name"]
            
            for option in variant["package_options"]:
                if stopped_by_user:
                    break
                    
                tokens = AuthInstance.get_active_tokens()
                option_order = option["order"]
                option_name = option["name"]
                option_price = option["price"]
                
                if not start_buying and option_order == start_from_option:
                    start_buying = True
                if not start_buying:
                    print(f"  {Colors.DIM_GREY}Skipping option {option_order}. {option['name']}{Colors.RESET}")
                    continue

                purchase_count += 1
                print(box_line(55))
                print(f"  {Colors.CYAN}Purchase {purchase_count} of {packages_count}...{Colors.RESET}")
                print(f"  {Colors.WHITE}Buying: {variant_name} - {option_order}. {option_name} - {Colors.YELLOW}Rp{option['price']}{Colors.RESET}")
                print(box_line(55))
                
                payment_items = []
                
                try:
                    if use_decoy:                
                        decoy = DecoyInstance.get_decoy("balance")
                        
                        decoy_package_detail = get_package(
                            api_key,
                            tokens,
                            decoy["option_code"],
                        )
                        
                        if not decoy_package_detail:
                            print(f"  {Colors.YELLOW}Failed to load decoy package details.{Colors.RESET}")
                            pause()
                            return False
                        
                        # Silent check inside loop - no prompt


                    target_package_detail = get_package_details(
                        api_key, tokens, family_code,
                        variant["package_variant_code"],
                        option["order"], None, None
                    )
                    
                    if not target_package_detail:
                        print(f"  {Colors.YELLOW}Failed to get package details. Skipping...{Colors.RESET}")
                        continue
                        
                except Exception as e:
                    print(f"  {Colors.RED}Exception: {e}{Colors.RESET}")
                    continue
                
                payment_items.append(
                    PaymentItem(
                        item_code=target_package_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=target_package_detail["package_option"]["price"],
                        item_name=str(randint(1000, 9999)) + " " + target_package_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=target_package_detail["token_confirmation"],
                    )
                )
                
                overwrite_amount = target_package_detail["package_option"]["price"]
                
                try:
                    res = settlement_balance(
                        api_key, tokens, payment_items, "🤑", False,
                        overwrite_amount=overwrite_amount,
                        token_confirmation_idx=0
                    )
                    
                    purchase_success = False
                    
                    if res and res.get("status", "") == "SUCCESS":
                        purchase_success = True
                    elif res and "Bizz-err.Amount.Total" in res.get("message", ""):
                        error_msg_arr = res.get("message", "").split("=")
                        valid_amount = int(error_msg_arr[1].strip())
                        print(f"Adjusted amount to: {valid_amount}")
                        
                        res = settlement_balance(
                            api_key, tokens, payment_items, "SHARE_PACKAGE", False,
                            overwrite_amount=valid_amount,
                            token_confirmation_idx=-1
                        )
                        if res and res.get("status", "") == "SUCCESS":
                            purchase_success = True
                    
                    if purchase_success:
                        package_info = f"{family_name} | {variant_name} | {option_order}. {option_name} - Rp{option_price}"
                        print(f"\n✅ BERHASIL: {package_info}")
                        
                        # Save to results folder
                        save_result_to_file(family_code, package_info, res)
                        all_successful_purchases.append({
                            "famcode": family_code,
                            "package": package_info
                        })
                        
                        # Ask user to continue
                        if pause_on_success:
                            print(box_line(55))
                            continue_choice = input(f"  {Colors.GREY}Lanjut ke paket selanjutnya? (y/t):{Colors.RESET} ").lower()
                            if continue_choice == "t":
                                stopped_by_user = True
                                print(f"  {Colors.YELLOW}Pembelian dihentikan oleh user.{Colors.RESET}")
                                break
                    else:
                        print(f"  {Colors.RED}Gagal: {res.get('message', 'Unknown error')}{Colors.RESET}")

                    if delay_seconds > 0 and not stopped_by_user:
                        print(f"  {Colors.DIM_GREY}Waiting {delay_seconds} seconds...{Colors.RESET}")
                        time.sleep(delay_seconds)

                        
                except Exception as e:
                    print(f"❌ Exception: {e}")
                    continue
    
    # Summary
    print(f"\n{'='*55}")
    print("RINGKASAN PEMBELIAN")
    print(f"{'='*55}")
    print(f"Total berhasil: {len(all_successful_purchases)}")
    
    if len(all_successful_purchases) > 0:
        print("\nDaftar paket berhasil dibeli:")
        for idx, item in enumerate(all_successful_purchases):
            print(f"{idx+1}. [{item['famcode']}] {item['package']}")
    
    print(f"{'='*55}")
    
    return len(all_successful_purchases) > 0

# Purchase
def purchase_by_family(
    family_code: str,
    use_decoy: bool,
    pause_on_success: bool = True,
    delay_seconds: int = 0,
    start_from_option: int = 1,
):
    active_user = AuthInstance.get_active_user()
    subscription_type = active_user.get("subscription_type", "")
    
    api_key = AuthInstance.api_key
    tokens: dict = AuthInstance.get_active_tokens() or {}
    
    if use_decoy:
        # Balance with Decoy
        decoy = DecoyInstance.get_decoy("balance")
        
        decoy_package_detail = get_package(
            api_key,
            tokens,
            decoy["option_code"],
        )
        
        if not decoy_package_detail:
            print("Failed to load decoy package details.")
            pause()
            return False
        
        balance_treshold = decoy_package_detail["package_option"]["price"]
        print(f"  {Colors.YELLOW}Pastikan sisa balance KURANG DARI Rp{balance_treshold}!!!{Colors.RESET}")
        balance_answer = input(f"  {Colors.GREY}Apakah anda yakin ingin melanjutkan pembelian? (y/n):{Colors.RESET} ")
        if balance_answer.lower() != "y":
            print(f"  {Colors.GREY}Pembelian dibatalkan oleh user.{Colors.RESET}")
            pause()
            return None
    
    family_data = get_family(api_key, tokens, family_code)
    if not family_data:
        print(f"Failed to get family data for code: {family_code}.")
        pause()
        return None
    
    family_name = family_data["package_family"]["name"]
    variants = family_data["package_variants"]
    
    print(section_header("PURCHASE BY FAMILY", 55))
    successful_purchases = []
    packages_count = 0
    for variant in variants:
        packages_count += len(variant["package_options"])
    
    purchase_count = 0
    start_buying = False
    if start_from_option <= 1:
        start_buying = True

    for variant in variants:
        variant_name = variant["name"]
        for option in variant["package_options"]:
            tokens = AuthInstance.get_active_tokens()
            option_order = option["order"]
            if not start_buying and option_order == start_from_option:
                start_buying = True
            if not start_buying:
                print(f"  {Colors.DIM_GREY}Skipping option {option_order}. {option['name']}{Colors.RESET}")
                continue
            
            option_name = option["name"]
            option_price = option["price"]
            
            purchase_count += 1
            print(box_line(55))
            print(f"  {Colors.CYAN}Purchase {purchase_count} of {packages_count}...{Colors.RESET}")
            print(f"  {Colors.WHITE}Buying: {variant_name} - {option_order}. {option_name} - {Colors.YELLOW}Rp{option['price']}{Colors.RESET}")
            print(box_line(55))
            
            payment_items = []
            
            try:
                if use_decoy:                
                    decoy = DecoyInstance.get_decoy("balance")
                    
                    decoy_package_detail = get_package(
                        api_key,
                        tokens,
                        decoy["option_code"],
                    )
                    
                    if not decoy_package_detail:
                        print("Failed to load decoy package details.")
                        pause()
                        return False
                
                target_package_detail = get_package_details(
                    api_key,
                    tokens,
                    family_code,
                    variant["package_variant_code"],
                    option["order"],
                    None,
                    None,
                )
            except Exception as e:
                print(f"Exception occurred while fetching package details: {e}")
                print(f"Failed to get package details for {variant_name} - {option_name}. Skipping.")
                continue
            
            payment_items.append(
                PaymentItem(
                    item_code=target_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=target_package_detail["package_option"]["price"],
                    item_name=str(randint(1000, 9999)) + " " + target_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=target_package_detail["token_confirmation"],
                )
            )
            
            if use_decoy:
                payment_items.append(
                    PaymentItem(
                        item_code=decoy_package_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=decoy_package_detail["package_option"]["price"],
                        item_name=str(randint(1000, 9999)) + " " + decoy_package_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=decoy_package_detail["token_confirmation"],
                    )
                )
            
            res = None
            
            overwrite_amount = target_package_detail["package_option"]["price"]
            if use_decoy or overwrite_amount == 0:
                overwrite_amount += decoy_package_detail["package_option"]["price"]
                
            error_msg = ""

            try:
                res = settlement_balance(
                    api_key,
                    tokens,
                    payment_items,
                    "🤑",
                    False,
                    overwrite_amount=overwrite_amount,
                    token_confirmation_idx=1
                )
                
                if res and res.get("status", "") != "SUCCESS":
                    error_msg = res.get("message", "")
                    if "Bizz-err.Amount.Total" in error_msg:
                        error_msg_arr = error_msg.split("=")
                        valid_amount = int(error_msg_arr[1].strip())
                        
                        print(f"Adjusted total amount to: {valid_amount}")
                        res = settlement_balance(
                            api_key,
                            tokens,
                            payment_items,
                            "SHARE_PACKAGE",
                            False,
                            overwrite_amount=valid_amount,
                            token_confirmation_idx=-1
                        )
                        if res and res.get("status", "") == "SUCCESS":
                            error_msg = ""
                            successful_purchases.append(
                                f"{variant_name}|{option_order}. {option_name} - {option_price}"
                            )
                            
                            if pause_on_success:
                                print("Purchase successful!")
                                pause()
                            else:
                                print("Purchase successful!")
                        else:
                            error_msg = res.get("message", "")
                else:
                    successful_purchases.append(
                        f"{variant_name}|{option_order}. {option_name} - {option_price}"
                    )
                    if pause_on_success:
                        print("Purchase successful!")
                        pause()
                    else:
                        print("Purchase successful!")

            except Exception as e:
                print(f"Exception occurred while creating order: {e}")
                res = None
            print("-------------------------------------------------------")
            if delay_seconds > 0:
                print(f"  {Colors.DIM_GREY}Waiting {delay_seconds} seconds...{Colors.RESET}")
                time.sleep(delay_seconds)
                
    print(f"Family: {family_name}\nSuccessful: {len(successful_purchases)}")
    if len(successful_purchases) > 0:
        print("-" * 55)
        print("Successful purchases:")
        for purchase in successful_purchases:
            print(f"- {purchase}")
    print("-" * 55)
    pause()

def purchase_n_times(
    n: int,
    family_code: str,
    variant_code: str,
    option_order: int,
    use_decoy: bool,
    delay_seconds: int = 0,
    pause_on_success: bool = False,
    token_confirmation_idx: int = 0,
):
    active_user = AuthInstance.get_active_user()
    subscription_type = active_user.get("subscription_type", "")
    
    api_key = AuthInstance.api_key
    tokens: dict = AuthInstance.get_active_tokens() or {}
    
    if use_decoy:
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
        
        balance_treshold = decoy_package_detail["package_option"]["price"]
        print(f"  {Colors.YELLOW}Pastikan sisa balance KURANG DARI Rp{balance_treshold}!!!{Colors.RESET}")
        balance_answer = input(f"  {Colors.GREY}Apakah anda yakin ingin melanjutkan pembelian? (y/n):{Colors.RESET} ")
        if balance_answer.lower() != "y":
            print(f"  {Colors.GREY}Pembelian dibatalkan oleh user.{Colors.RESET}")
            pause()
            return None
    
    family_data = get_family(api_key, tokens, family_code)
    if not family_data:
        print(f"Failed to get family data for code: {family_code}.")
        pause()
        return None
    family_name = family_data["package_family"]["name"]
    variants = family_data["package_variants"]
    target_variant = None
    for variant in variants:
        if variant["package_variant_code"] == variant_code:
            target_variant = variant
            break
    if not target_variant:
        print(f"Variant code {variant_code} not found in family {family_name}.")
        pause()
        return None
    target_option = None
    for option in target_variant["package_options"]:
        if option["order"] == option_order:
            target_option = option
            break
    if not target_option:
        print(f"Option order {option_order} not found in variant {target_variant['name']}.")
        pause()
        return None
    option_name = target_option["name"]
    option_price = target_option["price"]
    print(box_line(55))
    successful_purchases = []
    
    for i in range(n):
        print(f"  {Colors.CYAN}Purchase {i + 1} of {n}...{Colors.RESET}")
        print(f"  {Colors.WHITE}Buying: {target_variant['name']} - {option_order}. {option_name} - {Colors.YELLOW}{option_price}{Colors.RESET}")
        
        api_key = AuthInstance.api_key
        tokens: dict = AuthInstance.get_active_tokens() or {}
        
        payment_items = []
        
        try:
            if use_decoy:
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
            
            target_package_detail = get_package_details(
                api_key,
                tokens,
                family_code,
                target_variant["package_variant_code"],
                target_option["order"],
                None,
                None,
            )

        except Exception as e:
            print(f"  {Colors.RED}Exception occurred while fetching package details: {e}{Colors.RESET}")
            print(f"  {Colors.YELLOW}Failed to get package details for {target_variant['name']} - {option_name}. Skipping.{Colors.RESET}")
            continue
        
        payment_items.append(
            PaymentItem(
                item_code=target_package_detail["package_option"]["package_option_code"],
                product_type="",
                item_price=target_package_detail["package_option"]["price"],
                item_name=str(randint(1000, 9999)) + " " + target_package_detail["package_option"]["name"],
                tax=0,
                token_confirmation=target_package_detail["token_confirmation"],
            )
        )
        
        if use_decoy:
            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=str(randint(1000, 9999)) + " " + decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )
        
        res = None
        
        overwrite_amount = target_package_detail["package_option"]["price"]
        if use_decoy:
            overwrite_amount += decoy_package_detail["package_option"]["price"]

        try:
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                "🤫",
                False,
                overwrite_amount=overwrite_amount,
                token_confirmation_idx=token_confirmation_idx
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
                        token_confirmation_idx=token_confirmation_idx
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        successful_purchases.append(
                            f"{target_variant['name']}|{option_order}. {option_name} - {option_price}"
                        )
                        
                        if pause_on_success:
                            print("Purchase successful!")
                            pause()
                        else:
                            print("Purchase successful!")
            else:
                successful_purchases.append(
                    f"{target_variant['name']}|{option_order}. {option_name} - {option_price}"
                )
                if pause_on_success:
                    print("Purchase successful!")
                    pause()
                else:
                    print("Purchase successful!")
        except Exception as e:
            print(f"Exception occurred while creating order: {e}")
            res = None
        print(box_line(55))

        if delay_seconds > 0 and i < n - 1:
            print(f"  {Colors.DIM_GREY}Waiting {delay_seconds} seconds before next purchase...{Colors.RESET}")
            time.sleep(delay_seconds)

    print(f"Total successful purchases {len(successful_purchases)}/{n} for:\nFamily: {family_name}\nVariant: {target_variant['name']}\nOption: {option_order}. {option_name} - {option_price}")
    if len(successful_purchases) > 0:
        print("-------------------------------------------------------")
        print("Successful purchases:")
        for idx, purchase in enumerate(successful_purchases):
            print(f"{idx + 1}. {purchase}")
    print("-------------------------------------------------------")
    pause()
    return True

def purchase_n_times_by_option_code(
    n: int,
    option_code: str,
    use_decoy: bool,
    delay_seconds: int = 0,
    pause_on_success: bool = False,
    token_confirmation_idx: int = 0,
):
    active_user = AuthInstance.get_active_user()
    subscription_type = active_user.get("subscription_type", "")
    
    api_key = AuthInstance.api_key
    tokens: dict = AuthInstance.get_active_tokens() or {}
    
    if use_decoy:
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
        
        balance_treshold = decoy_package_detail["package_option"]["price"]
        print(f"  {Colors.YELLOW}Pastikan sisa balance KURANG DARI Rp{balance_treshold}!!!{Colors.RESET}")
        balance_answer = input(f"  {Colors.GREY}Apakah anda yakin ingin melanjutkan pembelian? (y/n):{Colors.RESET} ")
        if balance_answer.lower() != "y":
            print(f"  {Colors.GREY}Pembelian dibatalkan oleh user.{Colors.RESET}")
            pause()
            return None
    
    print(box_line(55))
    successful_purchases = []
    
    for i in range(n):
        print(f"  {Colors.CYAN}Purchase {i + 1} of {n}...{Colors.RESET}")
        
        api_key = AuthInstance.api_key
        tokens: dict = AuthInstance.get_active_tokens() or {}
        
        payment_items = []
        
        try:
            if use_decoy:
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
            
            target_package_detail = get_package(
                api_key,
                tokens,
                option_code,
            )
        except Exception as e:
            print(f"  {Colors.RED}Exception occurred while fetching package details: {e}{Colors.RESET}")
            continue
        
        payment_items.append(
            PaymentItem(
                item_code=target_package_detail["package_option"]["package_option_code"],
                product_type="",
                item_price=target_package_detail["package_option"]["price"],
                item_name=str(randint(1000, 9999)) + " " + target_package_detail["package_option"]["name"],
                tax=0,
                token_confirmation=target_package_detail["token_confirmation"],
            )
        )
        
        if use_decoy:
            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=str(randint(1000, 9999)) + " " + decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )
        
        res = None
        
        overwrite_amount = target_package_detail["package_option"]["price"]
        if use_decoy:
            overwrite_amount += decoy_package_detail["package_option"]["price"]

        try:
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                "🤫",
                False,
                overwrite_amount=overwrite_amount,
                token_confirmation_idx=token_confirmation_idx
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
                        token_confirmation_idx=token_confirmation_idx
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        successful_purchases.append(
                            f"Purchase {i + 1}"
                        )
                        
                        if pause_on_success:
                            print("Purchase successful!")
                            pause()
                        else:
                            print("Purchase successful!")
            else:
                successful_purchases.append(
                    f"Purchase {i + 1}"
                )
                if pause_on_success:
                    print("Purchase successful!")
                    pause()
                else:
                    print("Purchase successful!")
        except Exception as e:
            print(f"Exception occurred while creating order: {e}")
            res = None
        print("-------------------------------------------------------")

        if delay_seconds > 0 and i < n - 1:
            print(f"  {Colors.DIM_GREY}Waiting {delay_seconds} seconds before next purchase...{Colors.RESET}")
            time.sleep(delay_seconds)

    print(f"Total successful purchases {len(successful_purchases)}/{n}")
    if len(successful_purchases) > 0:
        print("-------------------------------------------------------")
        print("Successful purchases:")
        for idx, purchase in enumerate(successful_purchases):
            print(f"{idx + 1}. {purchase}")
    print("-------------------------------------------------------")
    pause()
    return True
