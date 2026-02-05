import os, argparse
from datetime import datetime

def compare_hex(original_path, dump_path, log_file):
    with open(original_path, "rb") as f1, open(dump_path, "rb") as f2:
        orig = f1.read()
        dump = f2.read()

    min_len = min(len(orig), len(dump))
    i = 0
    result = []

    while i < min_len:
        if orig[i] != dump[i]:
            result.append({
                "offset": hex(i),
                "orig": f"{orig[i]:02X}",
                "dump": f"{dump[i]:02X}"
            })
        i += 1

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["anogs", "hdmpve"])
    parser.add_argument("--dump", required=True)
    args = parser.parse_args()

    BASE = "BASE_LIBS"
    DUMP = "DUMP"

    base_map = {
        "anogs": "libanogs.so",
        "hdmpve": "libhdmpve.so"
    }

    base_lib = os.path.join(BASE, base_map[args.mode])
    dump_lib = os.path.join(DUMP, args.dump)

    if not os.path.isfile(base_lib):
        print("Base lib missing")
        return

    if not os.path.isfile(dump_lib):
        print("Dump lib missing")
        return

    result = compare_hex(base_lib, dump_lib, "logs/result.json")

    os.makedirs("logs", exist_ok=True)
    with open("logs/result.json", "w") as f:
        import json
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
