# ====================================================
#  🔧 ARPIT_OP Dump Tool V1.0 (FINAL FIX)
#  - SINGLE log.txt
#  - OLD LOG DELETE BEFORE EVERY DUMP
#  - REAL OFFSETS ONLY
# ====================================================

import os
import sys
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
    },
    "ue4": {                              # ✅ NEW
        "orig": "BASE_LIBS/libue4.so",     # base UE4 lib
        "start": 0x0,
        "end": 0xC0E1000                   # ✅ UE4 SIZE
    }
}


LOG_FILE = "logs/log.txt"   # 🔴 SINGLE LOG FILE (FIXED)

# ===================== LOGGER =======================

def log_offset(text):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {text}\n")

# ===================== BACKTRACE ====================

def match_backtrace(dump: bytes, offset: int):
    for back in range(8):
        pos = offset - back
        if pos < 0:
            continue

        if dump[pos:pos + len(PATTERN_FULL)] == PATTERN_FULL:
            return ("full", pos)

        if dump[pos:pos + len(PATTERN_PARTIAL)] == PATTERN_PARTIAL:
            return ("partial", pos)

    return (None, None)

# ===================== CORE COMPARE =================

def compare_hex(original_path, dump_path, start_offset, end_offset):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        original = f1.read()
        dump = f2.read()

    max_len = min(len(original), len(dump), end_offset)
    i = start_offset
    seen_offsets = set()

    # 🔴 LOG FILE ALWAYS STARTS FRESH
    with open(LOG_FILE, "w") as f:
        f.write(f"=== Log started at {datetime.now()} ===\n")

    while i < max_len:
        if original[i] != dump[i]:
            block_start = i

            # find continuous diff block
            while i < max_len and original[i] != dump[i]:
                i += 1

            block_len = i - block_start

            # -------- REAL HOOK --------
            if block_len > 8:
                if block_start not in seen_offsets:
                    log_offset(f"0x{block_start:06X} HOOK")
                    seen_offsets.add(block_start)
                continue

            # -------- PATTERN CHECK --------
            match_type, match_offset = match_backtrace(dump, block_start)

            if match_type and match_offset not in seen_offsets:
                if match_type == "full":
                    log_offset(
                        f"0x{match_offset:06X} 00 00 80 D2 C0 03 5F D6"
                    )
                else:
                    log_offset(
                        f"0x{match_offset:06X} C0 03 5F D6"
                    )
                seen_offsets.add(match_offset)

        else:
            i += 1

# ===================== MAIN ==========================

def main():
    parser = argparse.ArgumentParser(
        description="ARPIT_OP Dump Tool (FINAL CLEAN VERSION)"
    )
  parser.add_argument( "--mode",required=True, choices=["anogs", "hdmpve", "ue4"])  # ✅ ue4 added

    parser.add_argument("--dump", required=True)
    args = parser.parse_args()

    cfg = DUMP_CONFIG[args.mode]

    base_lib = cfg["orig"]
    start = cfg["start"]
    end = cfg["end"]

    dump_lib = os.path.join("DUMP", args.dump)

    # -------- SAFETY CHECKS --------
    if not os.path.isfile(base_lib):
        print("❌ Base library missing:", base_lib)
        sys.exit(1)

    if not os.path.isfile(dump_lib):
        print("❌ Dump library missing:", dump_lib)
        sys.exit(1)

    os.makedirs("logs", exist_ok=True)

    # 🔴 HARD DELETE OLD LOG BEFORE EVERY RUN
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    print("===================================")
    print(" ARPIT_OP Dump Tool (CLEAN MODE)")
    print(" Mode     :", args.mode.upper())
    print(" Base Lib :", base_lib)
    print(" Dump Lib :", dump_lib)
    print(f" Range    : 0x{start:X} - 0x{end:X}")
    print("===================================")
    print("[+] Starting scan...\n")

    compare_hex(base_lib, dump_lib, start, end)

    print("[✓] Scan finished")
    print("[✓] Log file:", LOG_FILE)

# ===================== ENTRY =========================

if __name__ == "__main__":
    main()

