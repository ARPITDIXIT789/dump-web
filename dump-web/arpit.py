# ====================================================
#  🔧 ARPIT_OP Dump Tool V1.0
#  REAL OFFSETS ONLY (ANOGS + HDMPVE)
# ====================================================

import os
import sys
import argparse
from datetime import datetime

# ====================================================
# PATTERNS (REAL)
# ====================================================

PATTERN_FULL = bytes.fromhex("00 00 80 D2 C0 03 5F D6")
PATTERN_PARTIAL = bytes.fromhex("C0 03 5F D6")

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
# LOGGER
# ====================================================

def log_offset(text, log_file):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {text}\n")

# ====================================================
# CORE COMPARE (FILTERED / REAL ONLY)
# ====================================================

def compare_hex(original_path, dump_path, start, end, log_file):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        orig = f1.read()
        dump = f2.read()

    max_len = min(len(orig), len(dump), end)
    i = start
    shown_offsets = set()

    os.makedirs("logs", exist_ok=True)
    with open(log_file, "w") as f:
        f.write(f"=== Log started at {datetime.now()} ===\n")

    while i < max_len:
        if orig[i] != dump[i]:
            block_start = i

            # find continuous diff block
            while i < max_len and orig[i] != dump[i]:
                i += 1

            block_len = i - block_start

            # =============================
            # REAL HOOK (long diff)
            # =============================
            if block_len >= 8:
                if block_start not in shown_offsets:
                    log_offset(f"0x{block_start:06X} HOOK", log_file)
                    shown_offsets.add(block_start)
                continue

            # =============================
            # BACKTRACE FOR REAL PATTERNS
            # =============================
            for back in range(8):
                off = block_start - back
                if off < 0 or off in shown_offsets:
                    continue

                # FULL PATTERN
                if dump[off:off + len(PATTERN_FULL)] == PATTERN_FULL:
                    log_offset(
                        f"0x{off:06X} 00 00 80 D2 C0 03 5F D6",
                        log_file
                    )
                    shown_offsets.add(off)
                    break

                # PARTIAL PATTERN
                if dump[off:off + len(PATTERN_PARTIAL)] == PATTERN_PARTIAL:
                    log_offset(
                        f"0x{off:06X} C0 03 5F D6",
                        log_file
                    )
                    shown_offsets.add(off)
                    break
        else:
            i += 1

# ====================================================
# MAIN
# ====================================================

def main():
    parser = argparse.ArgumentParser(
        description="ARPIT_OP Dump Tool (REAL OFFSETS ONLY)"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["anogs", "hdmpve"]
    )
    parser.add_argument(
        "--dump",
        required=True,
        help="Dumped .so filename inside DUMP/"
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
    print("[+] Scanning for REAL hooks...\n")

    compare_hex(
        original_path=base_lib,
        dump_path=dump_lib,
        start=start,
        end=end,
        log_file=log_file
    )

    print("[✓] Scan finished")
    print(f"[✓] Log saved at {log_file}")

# ====================================================
# ENTRY
# ====================================================

if __name__ == "__main__":
    main()
