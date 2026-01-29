from app.client.ciam import get_otp, submit_otp
from app.menus.util import clear_screen, pause
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special, info_line
from app.service.auth import AuthInstance

WIDTH = 55

def show_login_menu():
    clear_screen()
    print(section_header("LOGIN KE MYXL", WIDTH))
    print(menu_item("1", "Request OTP"))
    print(menu_item("2", "Submit OTP"))
    print(menu_item_special("99", "Tutup aplikasi"))
    print(box_line(WIDTH))
    
def login_prompt(api_key: str):
    clear_screen()
    print(section_header("LOGIN KE MYXL", WIDTH))
    print(f"  {Colors.GREY}Masukan nomor XL (Contoh 6281234567890):{Colors.RESET}")
    phone_number = input(f"  {Colors.GREY}Nomor:{Colors.RESET} ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        return None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            return None
        print("OTP Berhasil dikirim ke nomor Anda.")
        
        try_count = 5
        while try_count > 0:
            print(f"Sisa percobaan: {try_count}")
            otp = input("Masukkan OTP yang telah dikirim: ")
            if not otp.isdigit() or len(otp) != 6:
                print("OTP tidak valid. Pastikan OTP terdiri dari 6 digit angka.")
                continue
            
            tokens = submit_otp(api_key, "SMS", phone_number, otp)
            if not tokens:
                print("OTP salah. Silahkan coba lagi.")
                try_count -= 1
                continue
            
            print("Berhasil login!")
            return phone_number, tokens["refresh_token"]

        print("Gagal login setelah beberapa percobaan. Silahkan coba lagi nanti.")
        return None, None
    except Exception as e:
        print(f"Gagal login: {e}")
        return None, None

def show_account_menu():
    clear_screen()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()
        
    in_account_menu = True
    add_user = False
    while in_account_menu:
        clear_screen()
        print(box_line(WIDTH))
        print(section_header("AKUN TERSIMPAN", WIDTH))
        if not users or len(users) == 0:
            print(f"  {Colors.GREY}Tidak ada akun tersimpan.{Colors.RESET}")

        for idx, user in enumerate(users):
            is_active = active_user and user["number"] == active_user["number"]
            active_marker = f"{Colors.CYAN}✓{Colors.RESET}" if is_active else ""
            
            number = str(user.get("number", ""))
            number = number + " " * (14 - len(number))
            
            sub_type = user.get("subscription_type", "").center(12)
            print(f"  {Colors.CYAN}{idx + 1}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{number}{Colors.RESET} {Colors.GREY}[{sub_type}]{Colors.RESET} {active_marker}")
        
        print(box_line(WIDTH))
        print(section_header("COMMAND", WIDTH))
        print(menu_item("0", "Tambah Akun"))
        print(f"  {Colors.GREY}Masukan nomor urut akun untuk berganti.{Colors.RESET}")
        print(f"  {Colors.GREY}Masukan del <nomor urut> untuk menghapus.{Colors.RESET}")
        print(menu_item_special("00", "Kembali ke menu utama"))
        print(box_line(WIDTH))
        input_str = input(f"{Colors.GREY}Pilihan:{Colors.RESET} ")
        if input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None
        elif input_str == "0":
            phone, r_token = login_prompt(AuthInstance.api_key)
            if phone and r_token:
                # Assuming phone is int-compatible string or int
                 # login_prompt returns phone_number as string. add_refresh_token expects int usually?
                 # Let's check add_refresh_token signature in auth.py step 1118: def add_refresh_token(self, number: int, ...
                 # So convert to int.
                try:
                    AuthInstance.add_refresh_token(int(phone), r_token)
                    users = AuthInstance.refresh_tokens
                    active_user = AuthInstance.get_active_user()
                except Exception as e:
                    print(f"{Colors.RED}Gagal menyimpan token: {e}{Colors.RESET}")
                    pause()
            
            continue
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']
        elif input_str.startswith("del "):
            parts = input_str.split()
            if len(parts) == 2 and parts[1].isdigit():
                del_index = int(parts[1])
                
                # Prevent deleting the active user here
                if active_user and users[del_index - 1]["number"] == active_user["number"]:
                    print("Tidak dapat menghapus akun aktif. Silahkan ganti akun terlebih dahulu.")
                    pause()
                    continue
                
                if 1 <= del_index <= len(users):
                    user_to_delete = users[del_index - 1]
                    confirm = input(f"Yakin ingin menghapus akun {user_to_delete['number']}? (y/n): ")
                    if confirm.lower() == 'y':
                        AuthInstance.remove_refresh_token(user_to_delete["number"])
                        # AuthInstance.load_tokens()
                        users = AuthInstance.refresh_tokens
                        active_user = AuthInstance.get_active_user()
                        print("Akun berhasil dihapus.")
                        pause()
                    else:
                        print("Penghapusan akun dibatalkan.")
                        pause()
                else:
                    print("Nomor urut tidak valid.")
                    pause()
            else:
                print("Perintah tidak valid. Gunakan format: del <nomor urut>")
                pause()
            continue
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue