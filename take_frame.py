import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import os
import threading
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config_file = "config.ini"
config.read(config_file)

last_folder = config.get("settings", "last_folder", fallback="")

def save_last_folder(folder):
    config.set("settings", "last_folder", folder)
    with open(config_file, "w") as configfile:
        config.write(configfile)

def extract_frames(video_paths, output_folder, frame_rate, progress_bar, start_button):
    total_videos = len(video_paths)
    progress_per_video = 100 / total_videos
    
    # 将开始按钮设为不可用
    start_button.config(state="disabled")
    
    # 循环处理每个视频文件
    for index, video_path in enumerate(video_paths, start=1):
        # 打开视频文件
        video_capture = cv2.VideoCapture(video_path)
        
        # 获取视频帧率
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        
        # 计算抽帧间隔
        frame_interval = int(fps / frame_rate)

        # 初始化帧计数器
        frame_count = 0

        # 循环读取视频帧
        while True:
            ret, frame = video_capture.read()

            # 判断是否读取到帧
            if not ret:
                break

            # 如果是抽帧间隔的倍数，则保存帧
            if frame_count % frame_interval == 0:
                output_filename = os.path.join(output_folder, f"{os.path.basename(video_path)}_frame_{frame_count}.jpg")
                cv2.imwrite(output_filename, frame)

            # 更新帧计数器
            frame_count += 1

        # 释放视频对象
        video_capture.release()
        
        # 更新进度条
        progress_bar['value'] += progress_per_video
        progress_bar.update()
    
    # 将开始按钮设为可用
    start_button.config(state="normal")
    
    messagebox.showinfo("提示", "抽帧完成！")

def select_files():
    file_paths = filedialog.askopenfilenames(title="选择视频文件", filetypes=(("视频文件", "*.mp4 *.MOV"), ("所有文件", "*.*")), initialdir=last_folder)
    if file_paths:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, "\n".join(file_paths))
        # 保存选择的文件夹路径
        folder_path = os.path.dirname(file_paths[0])
        save_last_folder(folder_path)

def select_folder():
    folder_path = filedialog.askdirectory(title="选择保存文件夹", initialdir=last_folder)
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)
        # 保存选择的文件夹路径
        save_last_folder(folder_path)

def start_extraction():
    video_paths = file_entry.get().split("\n")
    output_folder = folder_entry.get()
    frame_rate = int(frame_rate_entry.get())
    
    # 如果保存文件夹路径不存在，则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 创建并启动线程
    extraction_thread = threading.Thread(target=extract_frames, args=(video_paths, output_folder, frame_rate, progress_bar, start_button))
    extraction_thread.start()

# 创建主窗口
root = tk.Tk()
root.title("视频帧抽取工具")

# 创建文件选择框和按钮
file_label = tk.Label(root, text="选择视频文件:")
file_label.grid(row=0, column=0, padx=5, pady=5)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=5, pady=5)
file_button = tk.Button(root, text="选择文件", command=select_files)
file_button.grid(row=0, column=2, padx=5, pady=5)

# 创建文件夹选择框和按钮
folder_label = tk.Label(root, text="选择保存文件夹:")
folder_label.grid(row=1, column=0, padx=5, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=1, column=1, padx=5, pady=5)
folder_button = tk.Button(root, text="选择文件夹", command=select_folder)
folder_button.grid(row=1, column=2, padx=5, pady=5)

# 创建帧率输入框和标签
frame_rate_label = tk.Label(root, text="帧率:")
frame_rate_label.grid(row=2, column=0, padx=5, pady=5)
frame_rate_entry = tk.Entry(root)
frame_rate_entry.grid(row=2, column=1, padx=5, pady=5)
frame_rate_entry.insert(0, "1")

# 创建开始按钮
start_button = tk.Button(root, text="开始抽帧", command=start_extraction)
start_button.grid(row=3, column=1, padx=5, pady=5)

# 创建进度条
progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress_bar.grid(row=4, columnspan=3, padx=5, pady=5)

# 运行主循环
root.mainloop()
