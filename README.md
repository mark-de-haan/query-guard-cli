# QueryGuard CLI 🛡️

**The Forensic Auditor for your BigQuery Bill.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**QueryGuard** (`bqg`) is a CLI tool that hunts down expensive BigQuery queries across your entire Google Cloud organization. It connects to the `INFORMATION_SCHEMA`, calculates exact costs based on regional pricing, and flags high-risk patterns like `SELECT *` or missing `LIMIT` clauses.

Stop guessing who spent the budget. **Know.**

---

## ⚡ Features

* **🌍 Global Auto-Discovery**: Automatically scans your project to find active regions and queries them in parallel. No more guessing if data is in `us-central1` or `europe-west3`.

* **💸 Forensic Cost Analysis**: Calculates costs based on the **exact datacenter pricing** (e.g., pricing Zurich queries at $8.75/TiB vs. US queries at $6.25/TiB).

* **🚩 Risk Detection**: Instantly flags bad habits:
    * `SELECT *` usage
    * Queries without `LIMIT`
    * Heavy scans (>100 GB)
    * Wrapper scripts vs. actual compute

* **🤖 Bot Filtering**: Use `--humans-only` to filter out service accounts and Looker bots, focusing strictly on manual engineering errors.
* **🚀 High Performance**: Uses multi-threaded execution to audit dozens of regions in seconds.

---

## 📦 Installation

### Option 1: Using Pip
```bash
pip install queryguard-cli
````

### Option 2: From Source (Poetry)
```bash
# Clone the repo
git clone git@github.com:mark-de-haan/query-guard-cli.git

# Navigate
cd queryguard-cli

# Install locally
poetry install
```

## 🚀 Quick Start
Ensure you are authenticated with Google Cloud:
```bash
gcloud auth application-default login
````

Run a forensic scan on your primary project for the last 7 days:
```bash
bqg scan --project my-gcp-project
```

#### Global scanning
Audit every active region globally to find hidden costs:
```bash
bqg scan --project my-gcp-project --global
```

## 🛠 Usage Guide
The `scan` Command
| Flag | Short | Description| 
| -----|-------|------------|
| --project | -p | Required. The GCP Project ID to audit. |
| --global | -g | Auto-discover active regions and scan them all in parallel. | 
| --region | -r | Scan a specific region (e.g., europe-west1). Ignored if --global is set. |
| --days | -d | Lookback window in days (Default: 7). | 
| --humans-only | | Hides service accounts (e.g., gserviceaccount, monitoring) to find manual errors. | 
| --limit | -l | Number of expensive queries to display (Default: 10). |

#### Examples
Find who is running expensive queries manually:
```bash
bqg scan -p my-data-warehouse --global --humans-only --days 30
```

Audit a specific region for a deep dive
```bash
bqg scan -p my-data-warehouse -r europe-west3
````

## 🤝 Contributing
Contributions are welcome! Please check the issues page.
1. Fork the Project
2. Create your Feature Branch (git checkout -b feat/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feat/AmazingFeature)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See LICENSE for more information.