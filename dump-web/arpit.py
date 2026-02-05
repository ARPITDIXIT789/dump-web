# ====================================================
#  🔧 ARPIT_OP Dump Tool V1.0 (ANOGS + HDMPVE ONLY)
# ====================================================

import os
import sys
import argparse
from datetime import datetime

# ====================================================
# CONFIG (ONLY REQUIRED MODES)
# ====================================================

DUMP_CONFIG = {
    "anogs": {
        "orig": "BASE_LIBS/libanogs.so",
        "start": 0x0,
        "end": 0x524680
    },
    "hdmpve": {
        "orig": "BASE_LIBS/libhdmpve.so",
        "start": 0x0,
        "end": 0x472394
    }
}

# ====================================================
# HELPERS
# ====================================================

def log_offset(line, log_file):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {line}\n")

# ====================================================
# CORE COMPARE (STRICT RANGE BASED)
# ====================================================

def compare_hex(original_path, dump_path, start, end, log_file):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        orig = f1.read()
        dump = f2.read()

    max_len = min(len(orig), len(dump), end)
    i = start

    os.makedirs("logs", exist_ok=True)
    with open(log_file, "w") as f:
        f.write(f"=== Compare Range: 0x{start:X} - 0x{end:X} ===\n")

    while i < max_len:
        if orig[i] != dump[i]:
            log_offset(
                f"0x{i:08X} {orig[i]:02X} -> {dump[i]:02X}",
                log_file
            )
        i += 1

# ====================================================
# MAIN
# ====================================================

def main():
    parser = argparse.ArgumentParser(
        description="ARPIT_OP Dump Tool (ANOGS + HDMPVE)"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["anogs", "hdmpve"],
        help="Dump type"
    )
    parser.add_argument(
        "--dump",
        required=True,
        help="Dumped .so file inside DUMP/"
    )
    args = parser.parse_args()

    cfg = DUMP_CONFIG[args.mode]

    base_lib = cfg["orig"]
    start = cfg["start"]
    end = cfg["end"]

    dump_lib = os.path.join("DUMP", args.dump)
    log_file = "logs/result.log"

    # SAFETY CHECKS
    if not os.path.isfile(base_lib):
        print(f"❌ Base library missing: {base_lib}")
        sys.exit(1)

    if not os.path.isfile(dump_lib):
        print(f"❌ Dump library missing: {dump_lib}")
        sys.exit(1)

    print("===================================")
    print(" ARPIT_OP Dump Tool")
    print(" Mode     :", args.mode.upper())
    print(" Base Lib :", base_lib)
    print(" Dump Lib :", dump_lib)
    print(f" Range    : 0x{start:X} - 0x{end:X}")
    print("===================================")
    print("[+] Starting compare...\n")

    compare_hex(
        original_path=base_lib,
        dump_path=dump_lib,
        start=start,
        end=end,
        log_file=log_file
    )

    print("[✓] Compare finished")
    print(f"[✓] Log saved at {log_file}")

# ====================================================
# ENTRY
# ====================================================

if __name__ == "__main__":
    main()
