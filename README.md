# Simple Finance Dashboard

## Overview
The Simple Finance Dashboard is a Streamlit-based web application designed to help users analyze their financial transactions by uploading bank statements in CSV or Excel format. It provides insights into income, expenses, savings rates, monthly trends, budgeting, and expense distribution, with interactive filtering and visualization capabilities. The app currently supports Paytm Passbook files (CSV and Excel formats) and can be extended to support other bank formats.

**Experience the dashboard live!** You can access the deployed application here:
[**https://financedashboard57.streamlit.app/**)

## Features
- **File Upload**: Supports Paytm Passbook in CSV and Excel formats for transaction data.
- **Financial Summary**: Displays total income, total expenses, net flow, and savings rate with a tooltip for clarity.
- **Monthly Trends**: Visualizes monthly income, expenses, and net flow using a line chart.
- **Monthly Budgeting**: Allows users to set a monthly expense budget and compare it with actual expenses, with a bar chart and a styled table showing budget differences.
- **Expense Distribution**: Shows a pie chart of expenses categorized by type (e.g., Food, Transport, Shopping).
- **Transaction Search & Filter**: Enables filtering by description, category, amount range, and date range, with a dynamic table displaying filtered transactions.
- **Top Transactions**: Lists the top 5 income and expense transactions based on the applied filters.

## Prerequisites
To run the Simple Finance Dashboard, ensure you have the following installed:
- Python 3.8 or higher
- Required Python packages (install via `pip`):
  ```bash
  pip install streamlit pandas numpy plotly openpyxl
  ```

## Installation
1. Clone or download the repository containing the dashboard code.
2. Navigate to the project directory:
   ```bash
   cd path/to/simple-finance-dashboard
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Alternatively, install the packages individually as listed in the Prerequisites section.
4. Ensure you have a Paytm Passbook file (CSV or Excel) to upload for analysis.

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```
   Replace `main.py` with the name of your Python script containing the dashboard code.
2. Open your web browser and navigate to the URL provided by Streamlit (typically `http://localhost:8501`).
3. Upload a Paytm Passbook file (CSV or Excel) using the file uploader.
4. Select the appropriate bank statement format from the dropdown (e.g., "Paytm Passbook (CSV)" or "Paytm Passbook (Excel)").
5. Explore the dashboard:
   - View the financial summary metrics (income, expenses, net flow, savings rate).
   - Analyze monthly trends via the line chart.
   - Set a monthly budget and compare it with actual expenses.
   - Inspect the expense distribution pie chart.
   - Use the search and filter tools to narrow down transactions by description, category, amount, or date range.
   - Review the top income and expense transactions.

## Project Snapshots
<img width="1920" height="1080" alt="Screenshot 2025-07-30 111616" src="https://github.com/user-attachments/assets/0b75a535-c1d4-473d-85b7-c5c34f3856dc" />
<img width="1920" height="1080" alt="Screenshot 2025-07-30 111645" src="https://github.com/user-attachments/assets/5115880d-0f08-4167-a37f-3a1f4785d09a" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0cc07a81-da82-4acd-a37f-222e99bdad0f" />

## File Format Requirements
The dashboard supports Paytm Passbook files with the following structure:
- **CSV or Excel**:
  - Columns: Must include `Date`, `Transaction Details`, `Amount`, and optionally `Tags` for categorization.
  - Date Format: `DD/MM/YYYY` (e.g., `25/12/2023`).
  - Amount: Single column representing both income (positive values) and expenses (negative values).
  - Tags: Optional Paytm tags (e.g., `#🛍 Shopping`) for initial categorization.

## Customization
To extend the dashboard for other bank formats:
1. Add a new configuration to the `BANK_CONFIGS` dictionary in the code, specifying:
   - File type (`csv` or `excel`)
   - Column names for date, description, amount, and optionally debit/credit columns
   - Date format
   - Header row and sheet name (for Excel)
   - Optional category column
2. Modify the `CATEGORY_RULES` dictionary to include keywords specific to your bank’s transaction descriptions.
3. Update the `refine_paytm_category` function to handle any bank-specific tags or categorization logic.

## Limitations
- Currently supports only Paytm Passbook formats (CSV and Excel).
- Assumes a single `Amount` column for Paytm files; separate debit/credit columns are supported but not used in the current configuration.
- Categorization relies on predefined keywords and Paytm tags, which may require tuning for accuracy.
- Date parsing assumes the `DD/MM/YYYY` format; other formats will need additional configuration.

## Future Improvements
- Add support for more bank formats (e.g., SBI, HDFC, ICICI).
- Enhance categorization with machine learning for more accurate transaction classification.
- Add export functionality for filtered transactions or summary reports.
- Include more advanced budgeting features, such as category-specific budgets.

## Troubleshooting
- **File Upload Errors**: Ensure the uploaded file matches the selected bank format and is not corrupted. Check for correct column names and date formats.
- **Visualization Issues**: Verify that all required Python packages (`plotly`, `pandas`, etc.) are installed.
- **Categorization Inaccuracies**: Review and update the `CATEGORY_RULES` dictionary to include more relevant keywords or refine Paytm tag mappings.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details (if applicable).

### Instructions for VS Code
1. Open VS Code.
2. Create a new file named `README.md` in your project directory.
3. Copy and paste the above content into the `README.md` file.
4. Save the file (`Ctrl + S` or `Cmd + S`).
5. The markdown will render properly in VS Code's preview mode (use `Ctrl + Shift + V` or `Cmd + Shift + V` to preview).
