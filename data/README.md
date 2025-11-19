# AQR Capital Management Factor Data

This directory contains datasets from AQR Capital Management's public data library.

**Source:** https://www.aqr.com/Insights/Datasets
**Download Date:** November 19, 2025
**Last Updated:** September 30, 2025 (as per AQR)

## Directory Structure

```
data/
├── README.md (this file)
├── aqr_raw/                      # Raw datasets from AQR
│   ├── Betting_Against_Beta/     # BAB factor data (3 files, ~33 MB)
│   ├── HML_Details/              # HML factor details (2 files, ~27 MB)
│   ├── Momentum_Indices/         # Momentum indices (1 file, 57 KB)
│   ├── Quality_Minus_Junk/       # QMJ quality factors (4 files, ~33 MB)
│   └── Value_and_Momentum_Everywhere/  # VME factors (3 files, ~1 MB)
│
└── scripts/                      # Data management scripts
    ├── download_aqr_data.py      # Download/update datasets from AQR
    └── preview_dataset.py        # Preview dataset contents
```

## Available Datasets (13 files total, ~93 MB)

### 1. Momentum Indices
Factor momentum strategies for U.S. large cap, small cap, and international markets.

**File:** `Momentum-Indices-Monthly.xlsx` (57 KB)

### 2. Betting Against Beta (BAB)
The "betting against beta" anomaly showing that low-beta stocks outperform high-beta stocks.

**Files:**
- `Betting-Against-Beta-Equity-Factors-Daily.xlsx` (30 MB) - Daily factors for U.S. and 23 international markets
- `Betting-Against-Beta-Equity-Factors-Monthly.xlsx` (2.4 MB) - Monthly factors
- `Betting-Against-Beta-Original-Paper-Data.xlsx` (145 KB) - Data from original research paper

### 3. The Devil in HML's Details
Updated value factors addressing construction issues in traditional HML.

**Files:**
- `The-Devil-in-HMLs-Details-Factors-Daily.xlsx` (25 MB) - Daily HML factors
- `The-Devil-in-HMLs-Details-Factors-Monthly.xlsx` (1.9 MB) - Monthly HML factors

Coverage: U.S. and 23 international equity markets

### 4. Quality Minus Junk (QMJ)
Quality factors based on profitability, growth, safety, and payout metrics.

**Files:**
- `Quality-Minus-Junk-Factors-Daily.xlsx` (30 MB) - Daily quality factors
- `Quality-Minus-Junk-Factors-Monthly.xlsx` (2.2 MB) - Monthly quality factors
- `Quality-Minus-Junk-Six-Portfolios-Formed-on-Size-and-Quality-Monthly.xlsx` (205 KB)
- `Quality-Minus-Junk-10-QualitySorted-Portfolios-Monthly.xlsx` (285 KB)

Time Coverage: U.S. from 1956, Global from 1986

### 5. Value and Momentum Everywhere
Value and momentum factors across multiple asset classes.

**Files:**
- `Value-and-Momentum-Everywhere-Factors-Monthly.xlsx` (249 KB)
- `Value-and-Momentum-Everywhere-Portfolios-Monthly.xlsx` (452 KB)
- `Value-and-Momentum-Everywhere-Original-Paper-Data.xlsx` (379 KB)

Coverage: Eight diverse markets and asset classes

## Setup (First Time Only)

Before using the data management scripts, you need to install Python dependencies:

### Option 1: Using the setup script (WSL/Linux/Mac)
```bash
cd /mnt/s/Projects/AQRFactorX/data/scripts
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual setup
```bash
cd S:\Projects\AQRFactorX\data\scripts

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On WSL/Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### List All Available Datasets
```bash
# From Windows (PowerShell):
cd S:\Projects\AQRFactorX\data\scripts
python preview_dataset.py

# From WSL:
cd /mnt/s/Projects/AQRFactorX/data/scripts
python preview_dataset.py
```

### Preview a Specific Dataset
```bash
python preview_dataset.py "S:\Projects\AQRFactorX\data\aqr_raw\Momentum_Indices\Momentum-Indices-Monthly.xlsx"
```

### Update Datasets (Re-download Latest from AQR)
```bash
cd S:\Projects\AQRFactorX\data\scripts
python download_aqr_data.py
```

### Using in Python
```python
import pandas as pd

# Read a dataset
file_path = r"S:\Projects\AQRFactorX\data\aqr_raw\Quality_Minus_Junk\Quality-Minus-Junk-Factors-Monthly.xlsx"
df = pd.read_excel(file_path, sheet_name='QMJ Factors')

# Most datasets have multiple sheets
excel_file = pd.ExcelFile(file_path)
print(excel_file.sheet_names)  # List all sheets

# Read specific sheet
df = pd.read_excel(file_path, sheet_name='Returns')
```

## Data Format

All files are in Excel format (.xlsx) with multiple sheets:
- **Disclosures Sheet:** Legal disclaimers and usage terms
- **Data Sheets:** Time series data with dates in first column, returns/factors in subsequent columns
- Most datasets include both U.S. and international market data

Typical columns:
- Date (first column, monthly or daily)
- Geographic regions (USA, Global, Europe, Japan, Asia Pacific ex Japan, etc.)
- Factor returns or portfolio returns

## Citation

When using these datasets in research or publications, please cite:
1. AQR Capital Management as the data source
2. The relevant research papers associated with each factor

Visit https://www.aqr.com/Insights/Datasets for publication details and proper citations.

## References

Key research papers:
- **Momentum:** Asness, Moskowitz, and Pedersen (2013)
- **Betting Against Beta:** Frazzini and Pedersen (2014)
- **Devil in HML's Details:** Asness and Frazzini (2013)
- **Quality Minus Junk:** Asness, Frazzini, and Pedersen (2019)
- **Value and Momentum Everywhere:** Asness, Moskowitz, and Pedersen (2013)

## Notes

- Data is provided by AQR for research and educational purposes
- Datasets are regularly updated by AQR (typically monthly)
- Historical data coverage varies by dataset (some go back to 1956)
- All returns assume reinvestment of dividends
- Returns do not reflect management fees, transaction costs, or other expenses
