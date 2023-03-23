import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def search_mac_address(directory_path, mac_address):
    results = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path, usecols=[0]) # 读取第一列
                    for index, row in df.iterrows():
                        if str(row[0]).lower() == mac_address.lower():
                            results.append({"file_path": file_path, "row_index": index})
                except Exception as e:
                    print(f"Error: {e}")
    return results

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # directory_path = request.form.get('directory_path')
        directory_path = r"/home/htekservice/workstation/hteksupport/mac/"
        mac_address = request.form.get('mac_address')
        results = search_mac_address(directory_path, mac_address)
        return render_template('result.html', results=results)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=8088, debug=True, host="0.0.0.0")
