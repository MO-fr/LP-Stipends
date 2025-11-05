Repository: Launchpad Pex & Rapid Stipend Transactions

## Overview
- This repository contains 5 CSV exports of Pex transaction data (FY2022-FY2026) and 1 Rapid transaction CSV
- **Total data**: 841 student stipend transactions from the Launchpad program (Foundations, 101, Summer sessions)
- **Workflow**: Merge all Pex + Rapid CSVs → Sort by student name → Export consolidated dataset
- One main Python script automates data processing: `merge_stipends.py`

## Architecture & Data Flow
```
Raw CSVs (6 files in Data/ folder)
    ├── Pex Transactions - FY2022.csv to FY2026.csv (5 files)
    └── Rapid Transaction.csv (1 file)
    ↓
scripts/merge_stipends.py → Data/processed/merged_stipends.csv (consolidated, sorted by name)
```

## Key Files & Patterns
**Input Files** (`Data/` folder):
- `Pex Transactions - FY2022.csv` (60 transactions)
- `Pex Transactions - FY2023.csv` (127 transactions)
- `Pex Transactions - FY2024.csv` (55 transactions)
- `Pex Transactions - FY2025.csv` (29 transactions)
- `Pex Transactions - FY2026.csv` (7 transactions)
- `Rapid Transaction.csv` (563 transactions)

**Scripts** (`scripts/` folder):
- `merge_stipends.py` - Merges all Pex + Rapid CSVs, filters columns, sorts by student name

**Output Files**:
- `Data/processed/merged_stipends.csv` - Consolidated dataset with Date, Name, Amount, Source columns

**CSV Header Patterns**:

*Pex Files:*
- **Standard columns**: `Date`, `Name`, `Amount`
- **Excluded columns**: `Created By`, `Method`, `Funding Request`, `Program`, `Business Account Transaction ID`, `Card Funding Transaction ID`, `Request ID`, `Comments`
- **Date format**: MM/DD/YYYY HH:MM AM/PM (e.g., "04/08/2022 11:46 AM")
- **Amount format**: Numeric, may be negative for reversals (e.g., -100)

*Rapid File:*
- **Source columns**: `date`, `transaction`, `Name`, `balance`
- **Mapped to**: `Date`, `Amount`, `Name` (balance excluded)
- **Date format**: M/D/YYYY (e.g., "3/28/2023")
- **Amount format**: Currency with $ and commas (e.g., "-$75.00")

*Output Format:*
- **Columns**: `Date`, `Name`, `Amount`, `Source`
- **Source values**: "Pex" or "Rapid"
- **Name format**: First Last (e.g., "Cheyenne Dumas")

## Critical Implementation Details
**Column Mapping** (handles both Pex and Rapid formats):
```python
# Pex files: Keep Date, Name, Amount as-is
# Rapid file: Map date→Date, transaction→Amount, keep Name
if is_rapid:
    df = df.rename(columns={'date': 'Date', 'transaction': 'Amount'})
    df = df[['Date', 'Name', 'Amount']].copy()
```

**Data Cleaning** (see `clean_amount()` function):
```python
# Remove dollar signs and commas from amounts
# Handle Pex: "$12,207,474,172.00" → 12207474172.00
# Handle Rapid: "-$75.00" → -75.0
amount_str = str(amount).replace('$', '').replace(',', '').strip()
return float(amount_str)
```

**Source Tracking**:
```python
# Add source column to track whether transaction is from Pex or Rapid
df['Source'] = 'Rapid' if is_rapid else 'Pex'
```

**Sorting Strategy**:
```python
# Sort by Name (alphabetical), then by Date (chronological within each name)
# Groups all transactions per student together (from both Pex and Rapid)
df = df.sort_values(by=['Name', 'Date'])
```

**CSV Parsing** (critical settings):
```python
# Use these pandas settings to handle varying column structures
pd.read_csv(file, encoding='utf-8', dtype=str)
```

## Developer Workflows

**Setup** (first time):
```bash
pip install pandas  # Only dependency
```

**Merge All Stipend Data**:
```bash
python scripts/merge_stipends.py
# Output: Data/processed/merged_stipends.csv (sorted by student name)
# Includes both Pex and Rapid transactions
```

**Inspect Headers Quickly**:
```bash
# Bash/Git Bash
head -n 1 Data/"Pex Transactions - FY2022.csv"

# PowerShell
Get-Content "Data\Pex Transactions - FY2022.csv" -TotalCount 1
```

**View Sample Output**:
```bash
# Bash/Git Bash
head -n 20 Data/processed/merged_stipends.csv

# PowerShell
Get-Content Data\processed\merged_stipends.csv -TotalCount 20
```

## Conventions & Gotchas
- **Two data sources** - Pex files (278 transactions) + Rapid file (563 transactions) = 841 total
- **Fiscal year numbering** - Pex files span FY2022-FY2026; check date ranges for actual chronology
- **Amount formatting varies** - Pex: may have $ and commas; Rapid: always has $ and negative sign (e.g., "-$75.00")
- **Negative amounts** - Common in Rapid (expenses); also in Pex for reversals/refunds
- **Column variations** - Pex files have varying columns across years; Rapid has different structure entirely
- **Date format differences** - Pex: "04/08/2022 11:46 AM"; Rapid: "3/28/2023" (no time)
- **Name overlaps** - Some students appear in both Pex and Rapid; all their transactions grouped together
- **Date sorting within names** - All transactions for one student grouped together chronologically (both Pex and Rapid)
- **Preserve original CSVs** - Never modify raw data in `Data/` folder; write outputs to `Data/processed/`

## Code Pattern Examples

**Read all Pex and Rapid files**:
```python
import glob
pex_files = glob.glob('Data/Pex Transactions - FY*.csv')
rapid_file = 'Data/Rapid Transaction.csv'
csv_files = pex_files + ([rapid_file] if os.path.exists(rapid_file) else [])
# Returns all 6 CSV files to merge
```

**Clean formatted currency values**:
```python
def clean_amount(amount):
    """Remove $ and commas, convert to float"""
    if pd.isna(amount) or amount == '':
        return 0.0
    amount_str = str(amount).replace('$', '').replace(',', '').strip()
    return float(amount_str)

df['Amount'] = df['Amount'].apply(clean_amount)
```

**Sort by name then date**:
```python
# Group all transactions per student, ordered chronologically
df = df.sort_values(by=['Name', 'Date'], ascending=[True, True])
df = df.reset_index(drop=True)
```

## When to Ask the User
- If analysis requires additional columns (e.g., Program from Pex, balance from Rapid)
- If date range filtering is needed (e.g., only FY2024-2025)
- If output format needs to change (e.g., JSON, Excel)
- If amount aggregation per student is desired
- If separate Pex vs Rapid analysis is needed (use Source column)
- If additional transaction files need to be included

## Quality Checks
After running the script, verify:
- `merged_stipends.csv` contains data from all 5 Pex fiscal years + Rapid file (6 sources total)
- Output has exactly 4 columns: Date, Name, Amount, Source
- Total transactions: 841 (278 Pex + 563 Rapid)
- Unique students: 138
- Data is sorted alphabetically by Name (all transactions for each student grouped together)
- Amounts are clean numeric values (no $ or commas)
- Source column shows "Pex" or "Rapid" for each transaction
- No excluded columns appear (Created By, Comments, balance, etc.)

## Example Output Structure
```csv
Date,Name,Amount,Source
01/25/2023 17:02PM,Ahmed Shamsid-Deen,75.0,Rapid
02/21/2023 18:58PM,Ahmed Shamsid-Deen,75.0,Rapid
3/28/2023,Ahmed Shamsid-Deen,-75.0,Rapid
07/25/2023 11:50 AM,Bryan Gunawan,165.0,Pex
10/13/2023 10:55 AM,Bryan Gunawan,165.0,Pex
7/11/2025,Bryan Gunawan,-5.0,Rapid
```
