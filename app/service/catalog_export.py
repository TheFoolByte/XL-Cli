import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.client.engsel import get_family
from app.client.store.search import get_family_list, get_store_packages
from app.client.store.segments import get_segments


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_token(text: str) -> str:
    token = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    token = token.strip("-")
    return token or "unknown"


def _extract_family_variants(family_data: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    variants_out: list[dict[str, Any]] = []
    total_options = 0

    for variant in family_data.get("package_variants", []):
        options_out: list[dict[str, Any]] = []
        for option in variant.get("package_options", []):
            options_out.append(
                {
                    "option_code": option.get("package_option_code", ""),
                    "option_name": option.get("name", ""),
                    "order": option.get("order", 0),
                    "price": option.get("price", 0),
                    "discounted_price": option.get("discounted_price", 0),
                    "validity": option.get("validity", ""),
                }
            )
            total_options += 1

        variants_out.append(
            {
                "variant_code": variant.get("package_variant_code", ""),
                "variant_name": variant.get("name", ""),
                "options": options_out,
            }
        )

    return variants_out, total_options


def export_package_catalog(
    api_key: str,
    tokens: dict[str, Any],
    subs_type: str,
    is_enterprise: bool = False,
    max_families: int = 0,
    include_store_search: bool = True,
    include_segments: bool = True,
    output_dir: str = "results",
    account_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started_at = _now_iso_utc()

    family_list_res = get_family_list(api_key, tokens, subs_type, is_enterprise)
    if not family_list_res:
        return {
            "status": "FAILED",
            "message": "Failed to fetch family list.",
            "path": "",
        }

    raw_family_items = family_list_res.get("data", {}).get("results", [])

    selected_families: list[dict[str, str]] = []
    seen_family_codes: set[str] = set()
    for family in raw_family_items:
        family_code = str(family.get("id", "")).strip()
        if family_code == "" or family_code in seen_family_codes:
            continue

        seen_family_codes.add(family_code)
        selected_families.append(
            {
                "family_code": family_code,
                "family_name": family.get("label", ""),
            }
        )

    if max_families > 0:
        selected_families = selected_families[:max_families]

    exported_families: list[dict[str, Any]] = []
    failed_families: list[dict[str, str]] = []
    total_options = 0

    total_family_candidates = len(selected_families)
    for idx, family_item in enumerate(selected_families, start=1):
        family_code = family_item["family_code"]
        family_name = family_item["family_name"]
        print(f"[catalog] Fetching family {idx}/{total_family_candidates}: {family_code} ({family_name})")

        requested_is_enterprise = True if is_enterprise else None
        family_data = get_family(
            api_key,
            tokens,
            family_code,
            is_enterprise=requested_is_enterprise,
            migration_type=None,
        )
        if not family_data:
            failed_families.append(
                {
                    "family_code": family_code,
                    "family_name": family_name,
                    "error": "Failed to fetch family detail",
                }
            )
            continue

        package_family = family_data.get("package_family", {})
        variants, family_option_count = _extract_family_variants(family_data)
        total_options += family_option_count

        exported_families.append(
            {
                "family_code": package_family.get("package_family_code", family_code),
                "family_name": package_family.get("name", family_name),
                "package_family_type": package_family.get("package_family_type", ""),
                "payment_for": package_family.get("payment_for", ""),
                "plan_type": package_family.get("plan_type", ""),
                "rc_bonus_type": package_family.get("rc_bonus_type", ""),
                "variant_count": len(variants),
                "option_count": family_option_count,
                "variants": variants,
            }
        )

    store_search_snapshot: list[dict[str, Any]] = []
    if include_store_search:
        store_res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
        if store_res and store_res.get("status") == "SUCCESS":
            for item in store_res.get("data", {}).get("results_price_only", []):
                store_search_snapshot.append(
                    {
                        "title": item.get("title", ""),
                        "family_name": item.get("family_name", ""),
                        "original_price": item.get("original_price", 0),
                        "discounted_price": item.get("discounted_price", 0),
                        "validity": item.get("validity", ""),
                        "action_type": item.get("action_type", ""),
                        "action_param": item.get("action_param", ""),
                    }
                )

    segments_snapshot: list[dict[str, Any]] = []
    if include_segments:
        segments_res = get_segments(api_key, tokens, is_enterprise)
        if segments_res and segments_res.get("status") == "SUCCESS":
            for segment in segments_res.get("data", {}).get("store_segments", []):
                segment_title = segment.get("title", "")
                for banner in segment.get("banners", []):
                    segments_snapshot.append(
                        {
                            "segment_title": segment_title,
                            "family_name": banner.get("family_name", ""),
                            "title": banner.get("title", ""),
                            "discounted_price": banner.get("discounted_price", 0),
                            "validity": banner.get("validity", ""),
                            "action_type": banner.get("action_type", ""),
                            "action_param": banner.get("action_param", ""),
                        }
                    )

    finished_at = _now_iso_utc()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ent_token = "enterprise" if is_enterprise else "retail"
    filename = f"catalog-{_safe_token(subs_type)}-{ent_token}-{timestamp}.json"

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / filename

    result_payload = {
        "meta": {
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "subs_type": subs_type,
            "is_enterprise": is_enterprise,
            "max_families": max_families,
            "include_store_search": include_store_search,
            "include_segments": include_segments,
            "family_list_total": len(raw_family_items),
            "family_selected_total": len(selected_families),
            "family_exported_total": len(exported_families),
            "family_failed_total": len(failed_families),
            "option_exported_total": total_options,
            "store_search_total": len(store_search_snapshot),
            "segments_total": len(segments_snapshot),
            "account": account_meta or {},
        },
        "family_list_snapshot": selected_families,
        "families": exported_families,
        "failed_families": failed_families,
        "store_search_snapshot": store_search_snapshot,
        "segments_snapshot": segments_snapshot,
    }

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)

    return {
        "status": "SUCCESS",
        "path": str(file_path),
        "family_exported_total": len(exported_families),
        "family_failed_total": len(failed_families),
        "option_exported_total": total_options,
        "store_search_total": len(store_search_snapshot),
        "segments_total": len(segments_snapshot),
    }
