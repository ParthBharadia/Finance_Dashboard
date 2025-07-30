import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
from io import StringIO

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

# --- 1. Bank Configuration ---
BANK_CONFIGS = {
    "Paytm Passbook (CSV)": {
        "file_type": "csv",
        "date_column": "Date",
        "description_column": "Transaction Details",
        "amount_column": "Amount",
        "header_row": 0,
        "date_format": "%d/%m/%Y",
        "category_column_from_source": "Tags"
    },

    "Paytm Passbook (Excel)": {
        "file_type": "excel",
        "sheet_name": "Passbook Payment History", # Specify the correct sheet name
        "date_column": "Date",
        "description_column": "Transaction Details",
        "amount_column": "Amount",
        "header_row": 0,
        "date_format": "%d/%m/%Y",
        "category_column_from_source": "Tags"
    }
}

# --- 2. Standardization Function ---
def standardize_statement(df, config):
    standard_df = pd.DataFrame()

    # Date - Modified to keep only the date part
    standard_df['Date'] = pd.to_datetime(df[config["date_column"]], format=config["date_format"], errors='coerce').dt.date

    # Description
    standard_df['Description'] = df[config["description_column"]].astype(str)

    # Amount (Handling separate debit/credit or single amount)
    if "debit_column" in config and "credit_column" in config:
        debit = pd.to_numeric(df[config["debit_column"]], errors='coerce').fillna(0)
        credit = pd.to_numeric(df[config["credit_column"]], errors='coerce').fillna(0)
        standard_df['Amount'] = credit - debit # Income as positive, expense as negative
    else:
        # This branch will be taken for Paytm as it has a single 'Amount' column
        standard_df['Amount'] = pd.to_numeric(df[config["amount_column"]], errors='coerce').fillna(0)

    # Infer Type (Income/Expense)
    standard_df['Type'] = standard_df['Amount'].apply(lambda x: 'Income' if x >= 0 else 'Expense')

    # Handle initial category from source if available
    if "category_column_from_source" in config and config["category_column_from_source"] in df.columns:
        # Paytm tags often start with '#', e.g., '#🛍 Shopping'
        standard_df['Initial_Category'] = df[config["category_column_from_source"]].astype(str).str.replace('#', '', regex=False).str.strip()
    else:
        standard_df['Initial_Category'] = 'Uncategorized' # Default if no source category

    # Calculate Running Balance (optional)
    standard_df['Balance'] = standard_df['Amount'].cumsum()

    return standard_df.dropna(subset=['Date', 'Amount']) # Drop rows where essential data is missing


# --- 3. Categorization Functions ---
CATEGORY_RULES = {
    'Food': ['swiggy', 'zomato', 'restaurant', 'cafe', 'dominos', 'pizza', 'fast food', 'soul tree'],
    'Transport': ['uber', 'ola', 'metro', 'fuel', 'petrol'],
    'Utilities': ['electricity', 'water bill', 'internet', 'broadband', 'telecom'],
    'Salary': ['salary', 'payout', 'employer', 'income'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'shopping'],
    'Rent': ['rent', 'house', 'landlord'],
    'Transfers': ['transfer', 'money sent', 'money received'], # For Paytm's 'Transfers'
    'Groceries': ['groceries', 'supermarket', 'kirana'],
    'Bills': ['bill', 'emi', 'payment'] # Added for general bills
}

def categorize_transaction_by_keyword(description):
    description_lower = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return 'Uncategorized'

def refine_paytm_category(paytm_tag, description, transaction_type):
    # Use Paytm's tag as a strong hint, then refine
    if paytm_tag and paytm_tag != 'nan': # Check for actual tag presence
        paytm_tag_lower = paytm_tag.lower()
        if 'shopping' in paytm_tag_lower: return 'Shopping'
        if 'food' in paytm_tag_lower: return 'Food'
        if 'groceries' in paytm_tag_lower: return 'Groceries'
        if 'transfers' in paytm_tag_lower: return 'Transfers'
        if 'income' in paytm_tag_lower or transaction_type == 'Income': return 'Income' # Ensure Income is caught
        if 'bill payment' in paytm_tag_lower: return 'Bills'
        if 'travel' in paytm_tag_lower: return 'Transport'
        if 'cashback' in paytm_tag_lower: return 'Income' # Treat cashback as income
        if 'recharge' in paytm_tag_lower: return 'Utilities' # Mobile/DTH recharge
        # Add more specific mappings for Paytm tags if you notice patterns
    
    # Fallback to general keyword-based categorization if Paytm tag isn't specific enough or absent
    return categorize_transaction_by_keyword(description)


# --- 4. Load Transactions Function ---
def load_transactions(uploaded_file, selected_bank_config):
    try:
        file_extension = uploaded_file.name.split('.')[-1]
        
        df_raw = None
        if file_extension == "csv": # No need to check selected_bank_config["file_type"] here
            df_raw = pd.read_csv(uploaded_file, skiprows=selected_bank_config.get("header_row", 0))
        elif file_extension in ["xlsx", "xls"]: # No need to check selected_bank_config["file_type"] here
            # Pass sheet_name if it exists in the config
            sheet_name = selected_bank_config.get("sheet_name", None)
            df_raw = pd.read_excel(uploaded_file, skiprows=selected_bank_config.get("header_row", 0), sheet_name=sheet_name)
        else:
            # This 'else' block should ideally not be hit if file_uploader types are controlled
            st.error(f"Unsupported file type: '{file_extension}'. Please upload a CSV or XLSX file.")
            return None

        if df_raw is None:
            return None
            
        df_standardized = standardize_statement(df_raw, selected_bank_config)
        
        # Apply intelligent categorization using Paytm's tags and custom rules
        df_standardized['Category'] = df_standardized.apply(
            lambda row: refine_paytm_category(row['Initial_Category'], row['Description'], row['Type']), axis=1
        )
        
        return df_standardized

    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.info("Please ensure the correct bank format is selected and the file is not corrupted.")
        return None

# --- 5. Main Streamlit Application ---
def main():
    st.title("💰 Simple Automated Finance Dashboard")
    st.write("Upload your bank statement to get started.")

    uploaded_file = st.file_uploader("Upload your transaction file (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Let user select bank type based on detected file type
        file_extension = uploaded_file.name.split('.')[-1]
        
        # Filter available configs based on file type
        # Display options based on the actual uploaded file's extension
        available_configs = {
            name: config for name, config in BANK_CONFIGS.items() 
            if (file_extension == "csv" and config["file_type"] == "csv") or \
               (file_extension in ["xlsx", "xls"] and config["file_type"] == "excel")
        }
        
        if not available_configs:
            st.warning(f"No bank configurations available for .{file_extension} files. Please ensure you have a configuration for this file type.")
            return # Exit if no suitable config

        bank_choice = st.selectbox("Select your bank statement format:", list(available_configs.keys()))
        selected_config = available_configs[bank_choice]

        df = load_transactions(uploaded_file, selected_config)

        if df is not None:
            st.subheader("Financial Summary")

            total_income = df[df['Type'] == 'Income']['Amount'].sum()
            total_expenses = abs(df[df['Type'] == 'Expense']['Amount'].sum())
            net_flow = total_income - total_expenses

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Income", f"₹{total_income:,.2f}")
            with col2:
                st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
            with col3:
                st.metric("Net Flow", f"₹{net_flow:,.2f}", delta=f"₹{net_flow:,.2f}" if net_flow != 0 else None)
            
            # New Feature: Savings Rate with tooltip
            savings_rate = 0
            if total_income > 0: # Avoid division by zero
                savings_rate = ((total_income - total_expenses) / total_income) * 100
            with col4:
                st.metric(
                    "Savings Rate", 
                    f"{savings_rate:.2f}%",
                    help="The percentage of your total income that remains after all expenses are deducted. Calculated as ((Total Income - Total Expenses) / Total Income) * 100."
                )


            # --- Monthly Trends ---
            st.subheader("Monthly Income vs. Expenses")
            # Using .dt.strftime('%Y-%m') for consistent month string for plotting and grouping
            df['Month'] = df['Date'].apply(lambda x: x.strftime('%Y-%m')) 
            monthly_summary = df.groupby(['Month', 'Type'])['Amount'].sum().unstack(fill_value=0)
            monthly_summary['Net'] = monthly_summary.get('Income', 0) + monthly_summary.get('Expense', 0)

            fig_monthly = px.line(monthly_summary.reset_index(), x='Month', y=['Income', 'Expense', 'Net'],
                                  title='Monthly Financial Flow',
                                  labels={'value': 'Amount (₹)', 'Month': 'Month'},
                                  color_discrete_map={'Income': 'green', 'Expense': 'red', 'Net': 'blue'},
                                  hover_name='Month')
            fig_monthly.update_traces(mode='lines+markers')
            st.plotly_chart(fig_monthly, use_container_width=True)

            # --- Basic Monthly Budgeting ---
            st.subheader("Monthly Budgeting")
            monthly_budget = st.number_input("Set your monthly expense budget (₹)", min_value=0.0, value=20000.0, step=1000.0)

            # Calculate actual monthly expenses
            monthly_actual_expenses = df[df['Type'] == 'Expense'].groupby('Month')['Amount'].sum().abs().reset_index()
            monthly_actual_expenses.columns = ['Month', 'Actual Expenses']
            
            # Ensure all months in summary are present in budget_df
            # Create a full list of months from the data for consistent display
            all_months_in_data = sorted(df['Month'].unique().tolist())
            monthly_budget_df = pd.DataFrame({'Month': all_months_in_data})
            
            monthly_budget_df = monthly_budget_df.merge(monthly_actual_expenses, on='Month', how='left').fillna(0)
            monthly_budget_df['Budget'] = monthly_budget
            monthly_budget_df['Difference'] = monthly_budget_df['Budget'] - monthly_budget_df['Actual Expenses']

            # Explanation for 'Difference' column
            st.info(
                "The 'Difference' column shows Budget - Actual Expenses. "
                "Green indicates you are under budget, while red indicates you are over budget."
            )

            # Display budget vs actual for each month
            # Changed background colors for better visibility
            styled_budget_df = monthly_budget_df.copy().style.applymap(
                lambda x: 'background-color: #FF6666' if x < 0 else 'background-color: #90EE90', # Brighter red for over budget, brighter green for under budget
                subset=['Difference']
            )
            st.dataframe(styled_budget_df, hide_index=True, use_container_width=True)

            fig_budget = px.bar(monthly_budget_df, x='Month', y=['Actual Expenses', 'Budget'],
                                title='Monthly Expenses vs. Budget',
                                labels={'value': 'Amount (₹)', 'Month': 'Month'},
                                barmode='group',
                                color_discrete_map={'Actual Expenses': 'red', 'Budget': 'green'})
            st.plotly_chart(fig_budget, use_container_width=True)

            # --- Expense Distribution ---
            st.subheader("Expense Distribution by Category")
            expenses_df = df[df['Type'] == 'Expense'].copy()
            expenses_df['Amount'] = expenses_df['Amount'].abs() # Make expenses positive for pie chart
            category_expenses = expenses_df.groupby('Category')['Amount'].sum().reset_index()

            fig_pie = px.pie(category_expenses, values='Amount', names='Category',
                             title='Expense Breakdown by Category',
                             hole=0.3,
                             hover_data=['Amount'])
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- Transaction Search and Filtering ---
            st.subheader("Transaction Search & Filter")
            
            # Get unique categories for multiselect
            all_categories = sorted(df['Category'].unique().tolist())
            
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                search_query = st.text_input("Search in Description (e.g., 'amazon', 'zomato')")
                selected_categories = st.multiselect("Filter by Category", options=all_categories, default=all_categories)
            with col_filter2:
                # Amount range slider
                min_amount, max_amount = float(df['Amount'].min()), float(df['Amount'].max())
                amount_range = st.slider("Filter by Amount Range (₹)", min_value=min_amount, max_value=max_amount, value=(min_amount, max_amount), format="₹%.2f")
                
                # Date range picker
                # Ensure min_date and max_date are actual date objects for st.date_input
                min_date_val = df['Date'].min()
                max_date_val = df['Date'].max()
                
                date_range = st.date_input("Filter by Date Range", 
                                            value=(min_date_val, max_date_val), 
                                            min_value=min_date_val, 
                                            max_value=max_date_val)
                
                # Ensure date_range has two dates before unpacking
                if len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    start_date, end_date = min_date_val, max_date_val # Default to full range if only one date selected


            filtered_df = df.copy()

            # Apply search query filter
            if search_query:
                filtered_df = filtered_df[filtered_df['Description'].str.contains(search_query, case=False, na=False)]

            # Apply category filter
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

            # Apply amount range filter
            filtered_df = filtered_df[(filtered_df['Amount'] >= amount_range[0]) & (filtered_df['Amount'] <= amount_range[1])]

            # Apply date range filter
            # Directly compare date objects since df['Date'] is now a date object
            filtered_df = filtered_df[
                (filtered_df['Date'] >= start_date) & 
                (filtered_df['Date'] <= end_date)
            ]

            st.dataframe(filtered_df[['Date', 'Description', 'Amount', 'Type', 'Category', 'Initial_Category', 'Balance']], use_container_width=True)


            # --- Top/Bottom Transactions (Apply filters if applicable, or show for entire data) ---
            st.subheader("Top Transactions (Filtered by above criteria)")
            col_income, col_expense = st.columns(2)
            with col_income:
                st.write("### Top Incomes")
                top_income = filtered_df[filtered_df['Type'] == 'Income'].nlargest(5, 'Amount')
                st.dataframe(top_income[['Date', 'Description', 'Amount', 'Category']], hide_index=True, use_container_width=True)
            with col_expense:
                st.write("### Top Expenses")
                # abs() is important here to get largest magnitude expenses for display
                top_expense = filtered_df[filtered_df['Type'] == 'Expense'].nsmallest(5, 'Amount') 
                st.dataframe(top_expense[['Date', 'Description', 'Amount', 'Category']], hide_index=True, use_container_width=True)


if __name__ == '__main__':
    main()