from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)

def calculate_daily_returns(df):
    """Calculate Daily Returns."""
    close_column = df.columns[df.columns.str.contains('Close', case=False)].tolist()
    if not close_column:
        raise KeyError("No column containing the word 'Close' found in the CSV file.")
    df['Daily Returns'] = df[close_column[0]].pct_change()
    return df

def calculate_daily_volatility(df):
    """Calculate Daily Volatility."""
    df['Daily Volatility'] = df['Daily Returns'].std()
    return df['Daily Volatility'].iloc[-1]

def calculate_annualized_volatility(daily_volatility, data_length):
    """Calculate Annualized Volatility."""
    return daily_volatility * np.sqrt(data_length)

def analyze_index_data(file_path):
    """
    Analyze historical index data.

    Parameters:
    - file_path (str): Path to the CSV file containing historical index data.

    Returns:
    - annualized_volatility (float): Annualized volatility.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Task 1: Calculate Daily Returns, Daily Volatility, and Annualized Volatility
    df = calculate_daily_returns(df)
    daily_volatility = calculate_daily_volatility(df)
    data_length = len(df)
    annualized_volatility = calculate_annualized_volatility(daily_volatility, data_length)

    return annualized_volatility

@app.route('/calculate_volatility', methods=['GET', 'POST'])
def calculate_volatility():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        try:
            # Save the uploaded file
            file_path = 'temp.csv'
            file.save(file_path)

            # Analyze the data and calculate volatility
            result = analyze_index_data(file_path)

            return jsonify({'annualized_volatility': result})
        
        except Exception as e:
            return jsonify({'error': f'Error processing the file: {str(e)}'}), 500
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
