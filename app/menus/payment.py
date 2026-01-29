from datetime import datetime, timedelta

from app.client.engsel import get_transaction_history
from app.menus.util import clear_screen
from app.menus.colors import Colors, section_header, box_line, menu_item, menu_item_special

WIDTH = 55

def show_transaction_history(api_key, tokens):
    in_transaction_menu = True

    while in_transaction_menu:
        clear_screen()
        print(section_header("RIWAYAT TRANSAKSI", WIDTH))

        data = None
        history = []
        try:
            data = get_transaction_history(api_key, tokens)
            history = data.get("list", [])
        except Exception as e:
            print(f"{Colors.YELLOW}Gagal mengambil riwayat transaksi: {e}{Colors.RESET}")
            history = []
        
        if len(history) == 0:
            print(f"  {Colors.GREY}Tidak ada riwayat transaksi.{Colors.RESET}")
        
        for idx, transaction in enumerate(history, start=1):
            transaction_timestamp = transaction.get("timestamp", 0)
            dt = datetime.fromtimestamp(transaction_timestamp)
            dt_jakarta = dt - timedelta(hours=7)

            formatted_time = dt_jakarta.strftime("%d %B %Y | %H:%M WIB")
            status = transaction['status']
            status_color = Colors.CYAN if status == "SUCCESS" else Colors.YELLOW

            print(f"  {Colors.CYAN}{idx}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{transaction['title']}{Colors.RESET} - {Colors.YELLOW}Rp {transaction['price']}{Colors.RESET}")
            print(f"     {Colors.GREY}Tanggal: {formatted_time}{Colors.RESET}")
            print(f"     {Colors.GREY}Metode: {transaction['payment_method_label']}{Colors.RESET}")
            print(f"     {Colors.GREY}Status: {status_color}{status}{Colors.RESET}")
            print(box_line(WIDTH))

        # Option
        print(menu_item("0", "Refresh"))
        print(menu_item_special("00", "Kembali ke Menu Utama"))
        print(box_line(WIDTH))
        choice = input(f"{Colors.GREY}Pilih opsi:{Colors.RESET} ")
        if choice == "0":
            continue
        elif choice == "00":
            in_transaction_menu = False
        else:
            print(f"{Colors.YELLOW}Opsi tidak valid.{Colors.RESET}")