import pandas as pd
import os
from typing import Dict


def generate_budget_spreadsheet(data: Dict, file_name: str) -> str:
    """
    Generate a structured spreadsheet from budget data.
    Returns the file path of the saved spreadsheet.
    """
    try:
        # Ensure the directory exists
        os.makedirs("./generated_budgets", exist_ok=True)

        # Creating a DataFrame from the budget data
        df = pd.DataFrame(data["details"].items(),
                          columns=["Category", "Amount"])
        summary = pd.DataFrame(
            data["summary"].items(), columns=["Metric", "Value"])

        # Saving to Excel
        file_path = f"./generated_budgets/{file_name}.xlsx"
        with pd.ExcelWriter(file_path) as writer:
            summary.to_excel(writer, sheet_name="Summary", index=False)
            df.to_excel(writer, sheet_name="Budget Details", index=False)

        return file_path
    except Exception as e:
        raise RuntimeError(f"Error generating spreadsheet: {str(e)}")
