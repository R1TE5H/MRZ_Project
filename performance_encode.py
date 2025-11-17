import json
import time
import csv
from pathlib import Path
from MRTD import viz_encoder as encode  # import your encode function

BASE_DIR = Path(__file__).resolve().parent


def load_records(filename):
    file_path = BASE_DIR / filename
    with open(file_path, "r") as f:
        data = json.load(f)

    if isinstance(data, dict) and "records_decoded" in data:
        return data["records_decoded"]
    return data


def encode_records(records, enable_tests):
    """
    enable_tests = True  → encode() runs with assertions/tests
    enable_tests = False → encode() runs without tests
    """
    encoded_output = []

    # Optionally disable tests by setting a flag your encode() function uses
    # If your encode() does not use a flag, we can monkey-patch assertions.
    if not enable_tests:
        import builtins
        builtins.assert_flag = False
    else:
        import builtins
        builtins.assert_flag = True

    for r in records:
        line1, line2 = encode(r)
        encoded_output.append(f"{line1};{line2}")

    return encoded_output


def measure_time(records, enable_tests):
    start = time.perf_counter()
    encode_records(records, enable_tests)
    end = time.perf_counter()
    return end - start


def main():
    # STEP 1: Load all decoded passport records
    all_records = load_records("records_decoded.json")

    # STEP 2: Define test sizes
    test_sizes = [100] + [i * 1000 for i in range(1, 11)]

    # STEP 3: Create CSV file
    with open(BASE_DIR / "timing_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["lines", "no_tests_sec", "with_tests_sec"])

        for k in test_sizes:
            subset = all_records[:k]

            print(f"Measuring for first {k} records...")

            # Without tests
            t_no_test = measure_time(subset, enable_tests=False)

            # With tests
            t_with_test = measure_time(subset, enable_tests=True)

            writer.writerow([k, t_no_test, t_with_test])

            print(f"  no tests:   {t_no_test:.4f}s")
            print(f"  with tests: {t_with_test:.4f}s")

    # STEP 4: Also save the full encoded output
    encoded_full = encode_records(all_records, enable_tests=True)
    with open(BASE_DIR / "records_encoded.json", "w") as f:
        for line in encoded_full:
            f.write(line + "\n")

    print("\nDone! timing_results.csv and records_encoded.json created.")


if __name__ == "__main__":
    main()
