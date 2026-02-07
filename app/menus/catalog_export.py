from pathlib import Path

from app.menus.colors import Colors, box_line, info_line, menu_item, menu_item_special, section_header
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
from app.service.catalog_export import export_package_catalog
from app.service.telegram_bot import send_file_notification
from app.service.decoy_template import (
    list_auto_target_profiles,
    build_decoy_payload,
    default_decoy_output_path,
    filter_options,
    infer_auto_profile_key,
    list_catalog_files,
    load_catalog_options,
    resolve_auto_decoy_output_path,
    write_decoy_payload,
)

WIDTH = 55
MAX_RENDERED_OPTIONS = 120


def _parse_non_negative_int(raw_value: str, fallback: int = 0) -> int:
    if raw_value == "":
        return fallback
    if not raw_value.isdigit():
        return fallback
    return int(raw_value)


def _parse_int_or_none(raw_value: str) -> int | None:
    raw = raw_value.strip()
    if raw == "":
        return None
    if raw.startswith("-"):
        return None
    if not raw.isdigit():
        return None
    return int(raw)


def _run_catalog_export(profile: dict):
    api_key = AuthInstance.api_key
    active_user = AuthInstance.get_active_user()
    tokens = AuthInstance.get_active_tokens()

    if not tokens or not active_user:
        print(f"{Colors.YELLOW}No active user tokens found.{Colors.RESET}")
        pause()
        return

    default_subs_type = str(profile.get("subscription_type", "PREPAID") or "PREPAID")

    clear_screen()
    print(section_header("EXPORT PACKAGE CATALOG", WIDTH))
    print(info_line("Nomor", active_user.get("number", "")))
    print(info_line("Type", active_user.get("subscription_type", "")))
    print(box_line(WIDTH))
    print(f"  {Colors.GREY}Kosongkan input untuk pakai nilai default.{Colors.RESET}")
    print(box_line(WIDTH))

    subs_type_input = input(f"  {Colors.GREY}Subs type [{default_subs_type}]:{Colors.RESET} ").strip().upper()
    subs_type = subs_type_input if subs_type_input else default_subs_type

    is_enterprise_input = input(f"  {Colors.GREY}Is enterprise? (y/n) [n]:{Colors.RESET} ").strip().lower()
    is_enterprise = is_enterprise_input == "y"

    max_families_input = input(f"  {Colors.GREY}Max families (0=all) [0]:{Colors.RESET} ").strip()
    max_families = _parse_non_negative_int(max_families_input, 0)

    include_store_input = input(f"  {Colors.GREY}Include store search snapshot? (y/n) [y]:{Colors.RESET} ").strip().lower()
    include_store_search = include_store_input != "n"

    include_segments_input = input(f"  {Colors.GREY}Include segments snapshot? (y/n) [y]:{Colors.RESET} ").strip().lower()
    include_segments = include_segments_input != "n"

    print(box_line(WIDTH))
    print(info_line("Subs Type", subs_type))
    print(info_line("Enterprise", "Yes" if is_enterprise else "No"))
    print(info_line("Max Families", str(max_families)))
    print(info_line("Store Snapshot", "Yes" if include_store_search else "No"))
    print(info_line("Segments Snapshot", "Yes" if include_segments else "No"))
    print(box_line(WIDTH))

    confirm = input(f"  {Colors.GREY}Jalankan export? (y/n):{Colors.RESET} ").strip().lower()
    if confirm != "y":
        print(f"{Colors.YELLOW}Export dibatalkan.{Colors.RESET}")
        pause()
        return

    print(f"{Colors.CYAN}Exporting catalog...{Colors.RESET}")
    result = export_package_catalog(
        api_key=api_key,
        tokens=tokens,
        subs_type=subs_type,
        is_enterprise=is_enterprise,
        max_families=max_families,
        include_store_search=include_store_search,
        include_segments=include_segments,
        account_meta={
            "number": active_user.get("number", ""),
            "subscriber_id": active_user.get("subscriber_id", ""),
            "subscription_type": active_user.get("subscription_type", ""),
        },
    )

    print(box_line(WIDTH))
    if result.get("status") != "SUCCESS":
        print(f"{Colors.RED}Export gagal.{Colors.RESET}")
        print(f"{Colors.GREY}{result.get('message', 'Unknown error')}{Colors.RESET}")
        print(box_line(WIDTH))
        pause()
        return

    print(f"{Colors.GREEN}Export selesai.{Colors.RESET}")
    print(info_line("File", result.get("path", "")))
    print(info_line("Families", str(result.get("family_exported_total", 0))))
    print(info_line("Failed", str(result.get("family_failed_total", 0))))
    print(info_line("Options", str(result.get("option_exported_total", 0))))
    print(info_line("Store Rows", str(result.get("store_search_total", 0))))
    print(info_line("Segments", str(result.get("segments_total", 0))))
    print(box_line(WIDTH))

    exported_file = result.get("path", "")
    if exported_file:
        caption = (
            f"Catalog export selesai\n"
            f"Type: {subs_type}\n"
            f"Enterprise: {is_enterprise}\n"
            f"Families: {result.get('family_exported_total', 0)}\n"
            f"Failed: {result.get('family_failed_total', 0)}"
        )
        send_file_notification(exported_file, caption=caption)

    ask_generate = input(f"  {Colors.GREY}Generate decoy template sekarang? (y/n):{Colors.RESET} ").strip().lower()
    if ask_generate == "y":
        _run_generate_decoy_template(
            result.get("path", ""),
            active_subscription_type=active_user.get("subscription_type", ""),
        )
        return

    pause()


def _pick_catalog_file(preselected_catalog_path: str = "") -> str | None:
    if preselected_catalog_path and Path(preselected_catalog_path).exists():
        return preselected_catalog_path

    files = list_catalog_files()
    if not files:
        print(f"{Colors.YELLOW}Belum ada file catalog di folder results/.{Colors.RESET}")
        pause()
        return None

    clear_screen()
    print(section_header("PILIH FILE CATALOG", WIDTH))
    for idx, file_path in enumerate(files, start=1):
        print(f"  {Colors.CYAN}{idx}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{file_path}{Colors.RESET}")
    print(box_line(WIDTH))

    picked = input(f"  {Colors.GREY}Pilih nomor file (00 batal):{Colors.RESET} ").strip()
    if picked == "00":
        return None
    if not picked.isdigit():
        print(f"{Colors.YELLOW}Input tidak valid.{Colors.RESET}")
        pause()
        return None

    picked_idx = int(picked)
    if picked_idx < 1 or picked_idx > len(files):
        print(f"{Colors.YELLOW}Nomor file di luar range.{Colors.RESET}")
        pause()
        return None

    return str(files[picked_idx - 1])


def _run_generate_decoy_template(preselected_catalog_path: str = "", active_subscription_type: str = ""):
    catalog_path = _pick_catalog_file(preselected_catalog_path)
    if not catalog_path:
        return

    try:
        loaded = load_catalog_options(catalog_path)
    except Exception as err:
        print(f"{Colors.RED}Gagal baca catalog file: {err}{Colors.RESET}")
        pause()
        return

    meta = loaded.get("meta", {})
    all_options = loaded.get("options", [])
    if len(all_options) == 0:
        print(f"{Colors.YELLOW}Catalog tidak punya opsi paket yang bisa dijadikan decoy.{Colors.RESET}")
        pause()
        return

    clear_screen()
    print(section_header("GENERATE DECOY TEMPLATE", WIDTH))
    print(info_line("Catalog", catalog_path))
    print(info_line("Subs Type", str(meta.get("subs_type", ""))))
    print(info_line("Enterprise", str(meta.get("is_enterprise", ""))))
    print(info_line("Total Opsi", str(len(all_options))))
    print(box_line(WIDTH))

    keyword = input(f"  {Colors.GREY}Filter keyword (opsional):{Colors.RESET} ").strip()
    filtered_options = filter_options(all_options, keyword)
    if len(filtered_options) == 0:
        print(f"{Colors.YELLOW}Tidak ada hasil untuk filter itu.{Colors.RESET}")
        pause()
        return

    shown_options = filtered_options[:MAX_RENDERED_OPTIONS]
    if len(filtered_options) > len(shown_options):
        print(
            f"{Colors.YELLOW}Hasil terlalu banyak ({len(filtered_options)}), ditampilkan {MAX_RENDERED_OPTIONS} teratas."
            f" Tambah keyword biar lebih spesifik.{Colors.RESET}"
        )
        print(box_line(WIDTH))

    for idx, item in enumerate(shown_options, start=1):
        print(
            f"  {Colors.CYAN}{idx}{Colors.DARK_GREY}.{Colors.RESET} "
            f"{Colors.WHITE}{item.get('family_name', '')} | {item.get('variant_name', '')}{Colors.RESET}"
        )
        print(
            f"     {Colors.GREY}{item.get('option_name', '')} | order {item.get('order', 0)}"
            f" | Rp{item.get('price', 0)}{Colors.RESET}"
        )
        print(f"     {Colors.DIM_GREY}family={item.get('family_code', '')}{Colors.RESET}")
        print(box_line(WIDTH))

    selected_input = input(f"  {Colors.GREY}Pilih opsi nomor (00 batal):{Colors.RESET} ").strip()
    if selected_input == "00":
        return
    if not selected_input.isdigit():
        print(f"{Colors.YELLOW}Input tidak valid.{Colors.RESET}")
        pause()
        return

    selected_idx = int(selected_input)
    if selected_idx < 1 or selected_idx > len(shown_options):
        print(f"{Colors.YELLOW}Nomor opsi di luar range.{Colors.RESET}")
        pause()
        return

    selected = shown_options[selected_idx - 1]
    default_price = int(selected.get("price", 0))

    payment_type = input(f"  {Colors.GREY}Payment type [balance/qris/qris0] (default balance):{Colors.RESET} ").strip().lower()
    if payment_type == "":
        payment_type = "balance"
    if payment_type not in ["balance", "qris", "qris0"]:
        print(f"{Colors.YELLOW}Payment type tidak valid, dipakai default balance.{Colors.RESET}")
        payment_type = "balance"

    migration_input = input(
        f"  {Colors.GREY}Migration type (kosong = null, contoh NONE/PRIOH_TO_PRIO):{Colors.RESET} "
    ).strip()
    migration_type = migration_input if migration_input != "" else None

    price_input = input(f"  {Colors.GREY}Price override (default {default_price}):{Colors.RESET} ").strip()
    price_override = _parse_int_or_none(price_input)

    output_mode = input(
        f"  {Colors.GREY}Output mode: auto by active type atau custom? [A/C] (default A):{Colors.RESET} "
    ).strip().lower()
    if output_mode == "":
        output_mode = "a"

    output_path = ""
    if output_mode == "a":
        auto_profiles = list_auto_target_profiles()
        inferred_profile = infer_auto_profile_key(active_subscription_type)
        auto_profile = inferred_profile if inferred_profile in auto_profiles else "default"
        shown_sub_type = active_subscription_type if active_subscription_type else "UNKNOWN"
        print(
            f"{Colors.CYAN}Auto profile from active subscription_type "
            f"({shown_sub_type}) -> {auto_profile}{Colors.RESET}"
        )

        resolved_path = resolve_auto_decoy_output_path(auto_profile, payment_type)
        if not resolved_path:
            resolved_path = default_decoy_output_path(auto_profile, payment_type)
        output_path = resolved_path
        print(f"{Colors.CYAN}Auto-map target: {output_path}{Colors.RESET}")
    else:
        profile_tag = input(f"  {Colors.GREY}Profile tag utk nama file (default custom):{Colors.RESET} ").strip()
        if profile_tag == "":
            profile_tag = "custom"
        default_out_path = default_decoy_output_path(profile_tag, payment_type)
        output_path_input = input(f"  {Colors.GREY}Output file [{default_out_path}]:{Colors.RESET} ").strip()
        output_path = output_path_input if output_path_input else default_out_path

    output_file = Path(output_path)
    if output_file.exists():
        overwrite = input(f"  {Colors.GREY}File sudah ada. Timpa? (y/n):{Colors.RESET} ").strip().lower()
        if overwrite != "y":
            print(f"{Colors.YELLOW}Generate dibatalkan.{Colors.RESET}")
            pause()
            return

    payload = build_decoy_payload(
        selected,
        migration_type=migration_type,
        price_override=price_override,
    )
    write_decoy_payload(payload, output_path)

    print(box_line(WIDTH))
    print(f"{Colors.GREEN}Decoy template berhasil dibuat.{Colors.RESET}")
    print(info_line("File", output_path))
    print(info_line("Family", payload.get("family_name", "")))
    print(info_line("Variant", selected.get("variant_name", "")))
    print(info_line("Option", payload.get("option_name", "")))
    print(info_line("Order", str(payload.get("order", 0))))
    print(info_line("Price", str(payload.get("price", 0))))
    print(box_line(WIDTH))
    pause()


def show_catalog_export_menu(profile: dict):
    while True:
        active_user = AuthInstance.get_active_user()
        clear_screen()
        print(section_header("CATALOG TOOLS", WIDTH))
        print(info_line("Nomor", (active_user or {}).get("number", "")))
        print(info_line("Type", (active_user or {}).get("subscription_type", "")))
        print(box_line(WIDTH))
        print(menu_item("1", "Export Package Catalog"))
        print(menu_item("2", "Generate Decoy Template"))
        print(menu_item_special("00", "Kembali"))
        print(box_line(WIDTH))

        choice = input(f"{Colors.GREY}Pilih menu:{Colors.RESET} ").strip()
        if choice == "1":
            _run_catalog_export(profile)
        elif choice == "2":
            _run_generate_decoy_template(
                active_subscription_type=(active_user or {}).get("subscription_type", "")
            )
        elif choice == "00":
            return
        else:
            print(f"{Colors.YELLOW}Pilihan tidak valid.{Colors.RESET}")
            pause()
