# ====================================================
#  🔧 ARPIT_OP Dump Tool V1.0 (FIXED – REAL ONLY)
# ====================================================

import os
import sys
import re
import argparse
from datetime import datetime

# ===================== PATTERNS =====================

PATTERN_FULL = bytes.fromhex("00 00 80 D2 C0 03 5F D6")
PATTERN_PARTIAL = bytes.fromhex("C0 03 5F D6")

# ===================== CONFIG =======================

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

# ===================== LOGGER =======================

def log_offset(line, log_file):
    with open(log_file, "a") as log:
        log.write(f"{datetime.now()} - {line}\n")

# ===================== BACKTRACE ====================

def match_backtrace(dump: bytes, offset: int):
    for back in range(8):
        check = offset - back
        if check < 0:
            continue

        if dump[check:check + len(PATTERN_FULL)] == PATTERN_FULL:
            return ("full", check)

        if dump[check:check + len(PATTERN_PARTIAL)] == PATTERN_PARTIAL:
            return ("partial", check)

    return (None, None)

# ===================== CORE COMPARE =================

def compare_hex(original_path, dump_path, start_offset, end_offset, log_file):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        original = f1.read()
        dump = f2.read()

    # 🔒 STRICT RANGE LIMIT
    max_len = min(len(original), len(dump), end_offset)
    i = max(0, start_offset)

    shown_offsets = set()

    with open(log_file, "w") as log:
        log.write(f"=== Log started at {datetime.now()} ===\n")

    while i < max_len:
        if original[i] != dump[i]:
            block_start = i

            # count continuous diff
            while i < max_len and original[i] != dump[i]:
                i += 1

            block_len = i - block_start

            # ========== REAL HOOK ==========
            if block_len > 8:
                if block_start not in shown_offsets:
                    log_offset(f"0x{block_start:06X} HOOK", log_file)
                    shown_offsets.add(block_start)
                continue

            # ========== PATTERN BACKTRACE ==========
            match_type, match_offset = match_backtrace(dump, block_start)

            if match_type and match_offset not in shown_offsets:
                if match_type == "full":
                    log_offset(
                        f"0x{match_offset:06X} 00 00 80 D2 C0 03 5F D6",
                        log_file
                    )
                else:
                    log_offset(
                        f"0x{match_offset:06X} C0 03 5F D6",
                        log_file
                    )
                shown_offsets.add(match_offset)

        else:
            i += 1

# ===================== MAIN ==========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["anogs", "hdmpve"])
    parser.add_argument("--dump", required=True)
    args = parser.parse_args()

    cfg = DUMP_CONFIG[args.mode]

    base_lib = cfg["orig"]
    start = cfg["start"]
    end = cfg["end"]

    dump_lib = os.path.join("DUMP", args.dump)
    log_file = "logs/result.log"

    if not os.path.isfile(base_lib):
        print("❌ Base lib missing:", base_lib)
        sys.exit(1)

    if not os.path.isfile(dump_lib):
        print("❌ Dump lib missing:", dump_lib)
        sys.exit(1)

    os.makedirs("logs", exist_ok=True)

    print("[+] Mode :", args.mode.upper())
    print("[+] Range:", hex(start), "-", hex(end))
    print("[+] Scanning...\n")

    compare_hex(base_lib, dump_lib, start, end, log_file)

    print("[✓] Done")
    print("[✓] Log saved:", log_file)

# ===================== ENTRY =========================

if __name__ == "__main__":
    main()
