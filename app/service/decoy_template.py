import json
from pathlib import Path
from typing import Any

AUTO_TARGET_PROFILE_MAP: dict[str, dict[str, str]] = {
    "default": {
        "balance": "default-balance",
        "qris": "default-qris",
        "qris0": "default-qris0",
    },
    "prio": {
        "balance": "prio-balance",
        "qris": "prio-qris",
        "qris0": "prio-qris0",
    },
    "priohybrid": {
        "balance": "priohybrid-balance",
        "qris": "prio-qris",
        "qris0": "prio-qris0",
    },
    "priopascabayar": {
        "balance": "priopascabayar-balance",
        "qris": "prio-qris",
        "qris0": "prio-qris0",
    },
    "go": {
        "balance": "priopascabayar-balance",
        "qris": "prio-qris",
        "qris0": "prio-qris0",
    },
}


def _safe_token(text: str) -> str:
    token = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    token = token.strip("-")
    return token or "custom"


def list_catalog_files(results_dir: str = "results") -> list[Path]:
    base = Path(results_dir)
    if not base.exists():
        return []
    return sorted(base.glob("catalog-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_catalog_options(catalog_path: str) -> dict[str, Any]:
    with open(catalog_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    meta = payload.get("meta", {})
    families = payload.get("families", [])

    options: list[dict[str, Any]] = []
    for family in families:
        family_code = family.get("family_code", "")
        family_name = family.get("family_name", "")
        for variant in family.get("variants", []):
            variant_code = variant.get("variant_code", "")
            variant_name = variant.get("variant_name", "")
            for option in variant.get("options", []):
                options.append(
                    {
                        "family_name": family_name,
                        "family_code": family_code,
                        "variant_name": variant_name,
                        "variant_code": variant_code,
                        "option_name": option.get("option_name", ""),
                        "order": option.get("order", 0),
                        "price": option.get("price", 0),
                        "is_enterprise": meta.get("is_enterprise"),
                    }
                )

    return {
        "meta": meta,
        "options": options,
    }


def filter_options(options: list[dict[str, Any]], keyword: str) -> list[dict[str, Any]]:
    keyword = keyword.strip().lower()
    if keyword == "":
        return options

    filtered: list[dict[str, Any]] = []
    for option in options:
        haystack = " | ".join(
            [
                str(option.get("family_name", "")),
                str(option.get("variant_name", "")),
                str(option.get("option_name", "")),
                str(option.get("family_code", "")),
                str(option.get("variant_code", "")),
            ]
        ).lower()
        if keyword in haystack:
            filtered.append(option)
    return filtered


def build_decoy_payload(
    selected_option: dict[str, Any],
    migration_type: str | None = None,
    price_override: int | None = None,
) -> dict[str, Any]:
    selected_price = selected_option.get("price", 0)
    price = selected_price if price_override is None else price_override

    return {
        "family_name": selected_option.get("family_name", ""),
        "family_code": selected_option.get("family_code", ""),
        "is_enterprise": selected_option.get("is_enterprise"),
        "migration_type": migration_type,
        "variant_code": selected_option.get("variant_code", ""),
        "option_name": selected_option.get("option_name", ""),
        "order": selected_option.get("order", 0),
        "price": price,
    }


def default_decoy_output_path(profile_tag: str, payment_type: str) -> str:
    return f"decoy_data/decoy-{_safe_token(profile_tag)}-{_safe_token(payment_type)}.json"


def list_auto_target_profiles() -> list[str]:
    return list(AUTO_TARGET_PROFILE_MAP.keys())


def infer_auto_profile_key(subscription_type: str) -> str:
    sub_type = (subscription_type or "").strip().upper()

    if sub_type == "PRIOHYBRID":
        return "priohybrid"
    if sub_type == "PRIORITAS":
        return "priopascabayar"
    if sub_type == "GO":
        return "go"
    return "default"


def resolve_auto_decoy_output_path(profile_key: str, payment_type: str) -> str | None:
    profile = AUTO_TARGET_PROFILE_MAP.get(profile_key)
    if not profile:
        return None
    decoy_name = profile.get(payment_type)
    if not decoy_name:
        return None
    return f"decoy_data/decoy-{decoy_name}.json"


def write_decoy_payload(payload: dict[str, Any], output_path: str):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        f.write("\n")
