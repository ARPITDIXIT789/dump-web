import sys
import json
from datetime import datetime

PATTERN_FULL = bytes.fromhex("00 00 80 D2 C0 03 5F D6")
PATTERN_PARTIAL = bytes.fromhex("C0 03 5F D6")

orig_path = sys.argv[1]
dump_path = sys.argv[2]
max_size = int(sys.argv[3], 16)
log_file = sys.argv[4]
json_file = sys.argv[5]

with open(orig_path, "rb") as f:
    orig = f.read()

with open(dump_path, "rb") as f:
    dump = f.read()

limit = min(len(orig), len(dump), max_size)
results = []

with open(log_file, "w") as log:
    log.write(f"=== Log started at {datetime.now()} ===\n")

i = 0
while i < limit:
    if orig[i] != dump[i]:
        start = i
        while i < limit and orig[i] != dump[i]:
            i += 1
        length = i - start

        if length > 8:
            results.append({"offset": hex(start), "type": "HOOK"})
            continue

        block = dump[start:start+8]
        if block.startswith(PATTERN_FULL):
            results.append({
                "offset": hex(start),
                "pattern": "FULL",
                "hex": block.hex(" ")
            })
        elif block.startswith(PATTERN_PARTIAL):
            results.append({
                "offset": hex(start),
                "pattern": "PARTIAL",
                "hex": block[:4].hex(" ")
            })
    else:
        i += 1

with open(json_file, "w") as jf:
    json.dump(results, jf, indent=2)

with open(log_file, "a") as log:
    for r in results:
        if "pattern" in r:
            log.write(f"{r['offset']} {r['hex']}\n")
        else:
            log.write(f"{r['offset']} HOOK\n")
