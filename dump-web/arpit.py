# ====================================================
#  🔧 ARPIT_OP Dump Tool V1.0 (AUTO MODE)
# ====================================================

import os, sys, re, argparse
from datetime import datetime

PATTERN_FULL = bytes.fromhex("00 00 80 D2 C0 03 5F D6")
PATTERN_PARTIAL = bytes.fromhex("C0 03 5F D6")

def log_offset(line, log_file):
    with open(log_file, "a") as log:
        log.write(f"{datetime.now()} - {line}\n")

def list_dump_files(directory="DUMP"):
    return [f for f in os.listdir(directory) if f.endswith(".so")]

def match_backtrace(dump: bytes, offset: int):
    for back in range(8):
        check = offset - back
        if check < 0:
            continue
        if dump[check:check+len(PATTERN_FULL)] == PATTERN_FULL:
            return ("full", check)
        if dump[check:check+len(PATTERN_PARTIAL)] == PATTERN_PARTIAL:
            return ("partial", check)
    return (None, offset)

def compare_hex(original_path, dump_path, start, end, log_file):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        orig = f1.read()
        dump = f2.read()

    min_len = min(len(orig), len(dump), end)
    i = start

    with open(log_file, "w") as log:
        log.write(f"=== Log started {datetime.now()} ===\n")

    while i < min_len:
        if orig[i] != dump[i]:
            start_i = i
            while i < min_len and orig[i] != dump[i]:
                i += 1
            if i - start_i > 8:
                log_offset(f"0x{start_i:04X} HOOK", log_file)
            else:
                match, off = match_backtrace(dump, start_i)
                if match:
                    hex_str = ' '.join(f"{b:02X}" for b in dump[off:off+4])
                    log_offset(f"0x{off:04X} {hex_str}", log_file)
        else:
            i += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["anogs", "hdmpve"])
    parser.add_argument("--dump", required=True)
    args = parser.parse_args()

    if args.mode == "anogs":
        orig = "anogs.so"
        start, end = 0x0, 0x520680
    else:
        orig = "HDMPVE.so"
        start, end = 0x0, 0x472394

    dump_path = os.path.join("DUMP", args.dump)
    log_file = "logs/uploaded_log.txt"

    if not os.path.isfile(dump_path):
        print("Dump not found")
        return

    compare_hex(orig, dump_path, start, end, log_file)

if __name__ == "__main__":
    main()
