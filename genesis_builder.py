from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

REPOSITORY_ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = REPOSITORY_ROOT / "data" / "fixtures" / "genesis_synthetic.json"
DEFAULT_OUTPUT_PATH = REPOSITORY_ROOT / "data" / "genesis_manifest.json"
MANIFEST_VERSION = "2.1.0-synthetic-demo"
ALLOWED_DATASET_CLASSES = {"SYNTHETIC_FIXTURE", "OBSERVED", "REPRODUCED"}


def canonical_json(value: Any) -> str:
    """Return the deterministic JSON representation used by the 2026-04-08 demo.

    The default JSON separators are intentionally retained for backwards-compatible
    record hashes and Merkle-root replay.
    """
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def omega_score(psi: float, theta_hat: float, cvar: float, pole: float) -> float:
    return 0.4 * psi + 0.3 * theta_hat + 0.2 * (1.0 - cvar) + 0.1 * pole


def get_decision(psi: float, omega: float, cvar: float) -> str:
    if psi < 0.85 or cvar > 0.05:
        return "BLOCK"
    if omega >= 0.85:
        return "PASS"
    return "CONDITIONAL"


def _bounded_number(record: Mapping[str, Any], field: str) -> int | float:
    raw = record.get(field)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValueError(f"{field} must be a number")
    if not 0.0 <= float(raw) <= 1.0:
        raise ValueError(f"{field} must be within [0, 1]")
    return raw


def normalize_input_record(record: Mapping[str, Any]) -> dict[str, Any]:
    name = record.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    psi = _bounded_number(record, "psi")
    cvar = _bounded_number(record, "cvar")
    theta_hat = _bounded_number(record, "theta_hat")
    pole = _bounded_number(record, "pole")
    omega = round(omega_score(float(psi), float(theta_hat), float(cvar), float(pole)), 4)

    normalized = {
        "name": name.strip(),
        "psi": psi,
        "cvar": cvar,
        "theta_hat": theta_hat,
        "pole": pole,
        "omega": omega,
        "decision": get_decision(float(psi), omega, float(cvar)),
    }
    normalized["h"] = sha256_json(normalized)
    return normalized


def compute_merkle_root(hashes: Sequence[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()

    layer = list(hashes)
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [
            hashlib.sha256((layer[index] + layer[index + 1]).encode("ascii")).hexdigest()
            for index in range(0, len(layer), 2)
        ]
    return layer[0]


def _timestamp_from_source_date_epoch() -> str | None:
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw is None:
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("SOURCE_DATE_EPOCH must be an integer Unix timestamp") from exc
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def resolve_timestamp(explicit: str | None) -> str:
    if explicit:
        parsed = datetime.fromisoformat(explicit.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return parsed.astimezone(timezone.utc).isoformat()

    reproducible = _timestamp_from_source_date_epoch()
    if reproducible is not None:
        return reproducible
    return datetime.now(timezone.utc).isoformat()


def load_dataset(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("dataset root must be an object")

    dataset_class = payload.get("dataset_class")
    if dataset_class not in ALLOWED_DATASET_CLASSES:
        raise ValueError(
            f"dataset_class must be one of {sorted(ALLOWED_DATASET_CLASSES)}"
        )

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty array")
    if not all(isinstance(item, dict) for item in records):
        raise ValueError("every record must be an object")

    source = payload.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("source must be an object")

    return {
        "dataset_class": dataset_class,
        "source": source,
        "records": records,
    }


def build_manifest(dataset: Mapping[str, Any], generated_at: str) -> dict[str, Any]:
    raw_records = dataset.get("records")
    if not isinstance(raw_records, list):
        raise ValueError("dataset records must be an array")

    records = [normalize_input_record(item) for item in raw_records]
    merkle_root = compute_merkle_root([record["h"] for record in records])
    dataset_class = str(dataset["dataset_class"])

    if dataset_class == "SYNTHETIC_FIXTURE":
        claim_scope = "LOCAL_DETERMINISTIC_DEMONSTRATION_ONLY"
        maturity = "TESTED_FIXTURE"
    elif dataset_class == "REPRODUCED":
        claim_scope = "REPRODUCED_WITHIN_DECLARED_ENVIRONMENT"
        maturity = "REPRODUCED"
    else:
        claim_scope = "OBSERVED_INPUTS_NOT_INDEPENDENTLY_REPRODUCED"
        maturity = "OBSERVED"

    source = dataset.get("source", {})
    if not isinstance(source, Mapping):
        raise ValueError("dataset source must be an object")

    return {
        "version": MANIFEST_VERSION,
        "generated_at": generated_at,
        "dataset_class": dataset_class,
        "claim_scope": claim_scope,
        "maturity": maturity,
        "source": dict(source),
        "merkle_root": merkle_root,
        "records": records,
    }


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    records = manifest.get("records")
    if not isinstance(records, list):
        raise ValueError("manifest records must be an array")

    hashes: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index} must be an object")
        stored_hash = record.get("h")
        if not isinstance(stored_hash, str):
            raise ValueError(f"record {index} is missing h")
        unhashed = dict(record)
        unhashed.pop("h")
        recomputed_hash = sha256_json(unhashed)
        if stored_hash != recomputed_hash:
            raise ValueError(f"record {index} hash mismatch")
        hashes.append(stored_hash)

    expected_root = compute_merkle_root(hashes)
    if manifest.get("merkle_root") != expected_root:
        raise ValueError("Merkle root mismatch")


def validate_replay(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be an object")
    validate_manifest(manifest)
    return manifest


def build_and_write(
    input_path: Path,
    output_path: Path,
    timestamp: str | None,
) -> dict[str, Any]:
    dataset = load_dataset(input_path)
    manifest = build_manifest(dataset, resolve_timestamp(timestamp))
    validate_manifest(manifest)
    atomic_write_json(output_path, manifest)
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or verify a MatVerse genesis demonstration manifest."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--timestamp",
        help="UTC ISO-8601 timestamp. Use this or SOURCE_DATE_EPOCH for exact replay.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the manifest at --output without rebuilding it.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.verify_only:
            manifest = validate_replay(args.output)
            print(f"PASS: {args.output} root={manifest['merkle_root']}")
            return 0

        manifest = build_and_write(args.input, args.output, args.timestamp)
        print(
            "PASS: genesis demonstration built "
            f"dataset_class={manifest['dataset_class']} "
            f"root={manifest['merkle_root']} "
            f"output={args.output}"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCK: {exc}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
