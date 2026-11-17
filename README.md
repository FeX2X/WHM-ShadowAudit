# WHM-ShadowAudit
🖥️ Advanced WHM authentication auditing toolkit built with Python. ⚡ Features multithreaded HTTP processing, session management, response validation, and real-time terminal statistics for authorized security assessments.

> 💀 **INTO THE SHADOWS. BEYOND THE FIREWALL.**

🐍 A Python-based WHM security auditing tool designed for authorized security assessments, featuring concurrent HTTP processing, session management, response analysis, and real-time terminal statistics.

## 🚀 Key Features

- ⚡ **Multithreading:** Concurrent processing using `ThreadPoolExecutor`.
- 🌐 **URL Normalization:** Automatically handles HTTPS and WHM port `2087`.
- 🔐 **HTTP Session Management:** Reuses HTTP sessions and TCP connections.
- 📡 **Authentication Response Analysis:** Examines server responses to identify authentication outcomes.
- 🎯 **Response Validation:** Checks for the `whm_zone_manager` response indicator.
- ⏱️ **Configurable Timeout:** Controls request timeout duration.
- 📊 **Live Statistics:** Displays checked, valid, invalid, and failed counts.
- 💾 **Automatic Result Export:** Saves matching results to `whm_valid.txt`.
- 🎨 **Colored Terminal:** Uses Colorama for clean, color-coded output.
- 🛡️ **Error Handling:** Handles timeouts and connection failures.

## 📂 Supported Input Format

The tool supports the following format:

```text
HOST|USERNAME|PASSWORD
```

### Example

```text
https://example.com:2087|username|password
example.com|username|password
```

**Input file:** `whm.txt`

## ⚙️ Requirements

- Python 3.8+
- requests
- colorama
- urllib3

## 📦 Installation

```bash
pip install requests colorama urllib3
```

## 💻 Usage

1. Place authorized test entries in `whm.txt`.
2. Install the required dependencies.
3. Run the script:

```bash
python whm.py
```

## 📁 Output

```text
whm_valid.txt
```

Contains entries that match the configured response-validation indicator.

## ⚡ Configuration

```python
INPUT_FILE = "whm.txt"
OUTPUT_VALID = "whm_valid.txt"

THREADS = 200
TIMEOUT = 30
```

- 🧵 `THREADS` — Maximum concurrent workers.
- ⏳ `TIMEOUT` — Maximum request wait time.
- 📥 `INPUT_FILE` — Input filename.
- 📤 `OUTPUT_VALID` — Output filename.

## ⚠️ Disclaimer

This project is intended strictly for authorized security auditing, educational purposes, and testing systems you own or have explicit permission to assess.

Do not use this tool against unauthorized WHM servers or credentials.

**🔒 Security First. Knowledge Is Power.**
