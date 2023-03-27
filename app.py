import os
from flask import Flask, render_template, request
import pandas as pd
from multiprocessing import Pool, Process, Queue


app = Flask(__name__)


def generate_file_list(root_directory_path):
    file_list = []
    for root, dirs, files in os.walk(root_directory_path):
        for file in files:
            if not file.startswith("~") and (file.endswith(".xlsx") or file.endswith(".xls")):
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    print(f"length of file list: {len(file_list)}")
    return file_list

# TODO: 优化搜索速度

def execute_search(mac_address, file_list, queue):
    print(f"{os.getpid()} run")
    results = []
    for file in file_list:
        # file_path = os.path.join(root, file)
        try:
            df = pd.read_excel(file, usecols=[0]) # 读取第一列
            for index, row in df.iterrows():
                if str(row[0]).lower() == mac_address.lower():
                    results.append({"file_path": file, "row_index": index})
                    print(results)
        except Exception as e:
            print(f"Error: {file}: {e}")
    # return results
    queue.put(results)

def search_mac_address(directory_path, mac_address):
    file_list = generate_file_list(directory_path)
    list_length = len(file_list)
    file_list_1 = file_list[0: list_length // 3]
    file_list_2 = file_list[list_length // 3: 2 * (list_length // 3)]
    file_list_3 = file_list[2 * (list_length // 3):]

    queue = Queue()
    p1 = Process(target=execute_search, args=(mac_address, file_list_1, queue))
    p2 = Process(target=execute_search, args=(mac_address, file_list_2, queue))
    p3 = Process(target=execute_search, args=(mac_address, file_list_3, queue))

    p1.start()
    p2.start()
    p3.start()

    r1 = queue.get()
    r2 = queue.get()
    r3 = queue.get()
    results = r1 + r2 + r3
    print(f"results: {results}")
    # p = Pool(3)
    # results = []
    # for _ in (file_list_1, file_list_2, file_list_3):
    #     res = p.apply_async(execute_search, args=(mac_address, _, ))
    #     results.append(res.get())
    # p.close()
    # p.join()
    # result = execute_search(mac_address, file_list)

    # results = []
    # for root, dirs, files in os.walk(directory_path):
    #     for file in files:
    #         if file.endswith(".xlsx") or file.endswith(".xls"):
    #             file_path = os.path.join(root, file)
    #             try:
    #                 df = pd.read_excel(file_path, usecols=[0]) # 读取第一列
    #                 for index, row in df.iterrows():
    #                     if str(row[0]).lower() == mac_address.lower():
    #                         results.append({"file_path": file_path, "row_index": index})
    #             except Exception as e:
    #                 print(f"Error: {e}")
    return results


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # directory_path = request.form.get('directory_path')
        # directory_path = r"/home/htekservice/workstation/hteksupport/mac/"
        directory_path = r"G:\HtekRepo\experiment\hteksupport\mac"
        mac_address = request.form.get('mac_address')
        results = search_mac_address(directory_path, mac_address)
        print(f"file path: {results[0]['file_path']}")
        return render_template('result.html', results=results)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=8088, debug=True, host="0.0.0.0")
