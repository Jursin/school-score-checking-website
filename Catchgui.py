from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import tkinter as tk
from tkinter import filedialog

def create_gui():
    root = tk.Tk()
    root.title("成绩抓取")

    tk.Label(root, text="输入网址:").grid(row=0, column=0, padx=10, pady=10)
    url_entry = tk.Entry(root, width=50)
    url_entry.grid(row=0, column=1, padx=10, pady=10)

    def select_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        excel_entry.delete(0, tk.END)
        excel_entry.insert(0, file_path)

    tk.Label(root, text="选择Excel文件:").grid(row=1, column=0, padx=10, pady=10)
    excel_entry = tk.Entry(root, width=50)
    excel_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="选择文件", command=select_excel).grid(row=1, column=2, padx=10, pady=10)

    def select_output():
        folder_path = filedialog.askdirectory()
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

    tk.Label(root, text="选择输出文件夹:").grid(row=2, column=0, padx=10, pady=10)
    output_entry = tk.Entry(root, width=50)
    output_entry.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(root, text="选择文件夹", command=select_output).grid(row=2, column=2, padx=10, pady=10)

    tk.Label(root, text="输出文件名:").grid(row=3, column=0, padx=10, pady=10)
    filename_entry = tk.Entry(root, width=50)
    filename_entry.grid(row=3, column=1, padx=10, pady=10)

    # 创建一个 Frame 用于存放按钮
    button_frame = tk.Frame(root)
    button_frame.grid(row=4, column=0, columnspan=3, pady=20)

    def on_submit():
        url = url_entry.get()
        excel_file = excel_entry.get()
        output_folder = output_entry.get()
        filename = filename_entry.get()
        root.destroy()
        main_process(url, excel_file, output_folder, filename)

    # 创建"开始抓取"按钮并设置大小、间距
    submit_button = tk.Button(button_frame, text="开始抓取", command=on_submit, width=15)
    submit_button.pack(side=tk.LEFT, padx=10)

    cancel_button = tk.Button(button_frame, text="取消", command=root.quit, width=15)
    cancel_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()

def main_process(url, excel_file, output_folder, filename):
    try:
        df = pd.read_excel(excel_file)
        print(f"Excel file loaded: {excel_file}")

        driver = webdriver.Edge()
        driver.get(url)
        print(f"Opened URL: {url}")

        output_data = []

        for index, row in df.iterrows():
            data1 = row[1]  # 从 Excel 表格中读取第二列的值
            data2 = str(row[2])[-4:]  # 从 Excel 表格中读取第三列的后四位

            # 定位并输入数据到网页的输入框中
            input1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 's_xingming')))  # 定位第一个输入框
            input2 = driver.find_element(By.NAME, 's_chaxunma')  # 定位第二个输入框

            input1.clear()  # 清除第一个输入框中的内容
            input2.clear()  # 清除第二个输入框中的内容

            input1.send_keys(str(data1))  # 将 data1 输入到第一个输入框
            input2.send_keys(str(data2))  # 将 data2 输入到第二个输入框

            # 定位带有“查询”字样的按钮并点击
            submit_button = driver.find_element(By.XPATH, '//button[contains(text(),"查询")]')
            submit_button.click()

            # 等待页面加载
            time.sleep(0.5)

            # 抓取输出并保存
            elements = driver.find_elements(By.CLASS_NAME, 'right_cell')  # 查找所有包含输出数据的元素
            output_values = [element.text for element in elements]  # 提取所有元素的文本
            output_data.append([data1, data2] + output_values)  # 将 data1, data2 和所有输出值作为一行数据添加到 output_data 中

            driver.get(url)  # 返回初始网址
            time.sleep(0.5)  # 等待页面加载

        save_output(output_data, output_folder, filename)
        print(f"Data saved to {output_folder}/{filename}.xlsx")

    except Exception as e:
        print(f"An error occurred: {e}")

    driver.quit()

def save_output(output_data, output_folder, filename):
    file_path = os.path.join(output_folder, f"{filename}.xlsx")

    # 创建 DataFrame
    output_df = pd.DataFrame(output_data)

    # 如果文件已存在，尝试读取现有数据并更新
    if os.path.exists(file_path):
        try:
            existing_df = pd.read_excel(file_path, engine='openpyxl', header=None)
            updated_df = pd.concat([existing_df, output_df], ignore_index=True)
        except ValueError:
            updated_df = output_df
    else:
        updated_df = output_df

    # 保存更新后的 DataFrame 到 Excel 文件，不包含列头
    updated_df.to_excel(file_path, index=False, header=False, engine='openpyxl')

if __name__ == "__main__":
    create_gui()