import pandas as pd
import uuid
import os

def create_bills_file():
    """
    This script reads an original source file (MAINBILL.TXT or MAINBILL.csv),
    handles character encoding issues, cleans the data, adds a unique
    billuuid, and saves the result as bills.csv.
    """
    print("Starting process to create 'bills.csv'...")

    source_filename = None
    if os.path.exists('MAINBILL.TXT'):
        source_filename = 'MAINBILL.TXT'
    elif os.path.exists('MAINBILL.csv'):
        source_filename = 'MAINBILL.csv'
    else:
        print("\nError: Could not find 'MAINBILL.TXT' or 'MAINBILL.csv'.")
        print("Please make sure your original source file for bills is in the same folder as this script.")
        return

    try:
        print(f"Found and loading source file: {source_filename}")
        
        # --- THIS IS THE FIX ---
        # Added encoding='latin1' to handle special characters in the source file.
        mainbill_df = pd.read_csv(source_filename, encoding='latin1')
        
        print("File loaded successfully with new encoding.")

        # --- Data Cleaning ---
        original_rows = len(mainbill_df)
        mainbill_df['BillNumber'] = pd.to_numeric(mainbill_df['BillNumber'], errors='coerce')
        mainbill_df.dropna(subset=['BillNumber', 'BillType'], inplace=True)
        mainbill_df['BillNumber'] = mainbill_df['BillNumber'].astype(int)
        
        cleaned_rows = len(mainbill_df)
        print(f"Removed {original_rows - cleaned_rows} rows with invalid BillNumber or BillType.")

        date_columns = ['LDOA', 'IntroDate', 'GovernorDateOfAction', 'EffectiveDate', 'ProposedDate', 'ModDate']
        for col in date_columns:
            mainbill_df[col] = pd.to_datetime(mainbill_df[col], errors='coerce')
        print("Date columns converted.")

        mainbill_df['billuuid'] = [uuid.uuid4() for _ in range(len(mainbill_df))]
        print("Unique 'billuuid' column added.")

        mainbill_df.to_csv('bills.csv', index=False)
        print("\n✅ Successfully created 'bills.csv'.")
        print("You can now run the 'generate_corrected_files.py' script.")

    except Exception as e:
        print(f"\nAn unexpected error occurred while processing the file: {e}")
        return

if __name__ == '__main__':
    create_bills_file()