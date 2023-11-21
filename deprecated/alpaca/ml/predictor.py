import pandas as pd


def predict(df, clf):
    # Initialize an empty dataframe to store results
    columns = ['date', 'MACD', 'MACD_signal', 'Bollinger_High', 'Bollinger_Low', 'VWAP', 'prediction', 'actual_outcome']
    results_df = pd.DataFrame(columns=columns)

    # Each time you make a prediction, append to the dataframe
    # Assuming 'df' is your current data and 'prediction' is the output of your model
    for index, row in df.iterrows():
        prediction = clf.predict([row[['MACD', 'MACD_signal', 'Bollinger_High', 'Bollinger_Low', 'VWAP']].values])[0]
        actual_outcome = row['Target']

        results_df = results_df.append({
            'date': index,
            'MACD': row['MACD'],
            'MACD_signal': row['MACD_signal'],
            'Bollinger_High': row['Bollinger_High'],
            'Bollinger_Low': row['Bollinger_Low'],
            'VWAP': row['VWAP'],
            'prediction': prediction,
            'actual_outcome': actual_outcome
        }, ignore_index=True)

    # Save to CSV for future analysis
    results_df.to_csv('model_results.csv', index=False)


