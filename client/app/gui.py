import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from utils import discover_gpus, submit_training_job

class ApplicationGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Section for GPU discovery
        self.discover_frame = ttk.LabelFrame(self, text="Discover GPUs")
        self.discover_frame.pack(fill="x", padx=10, pady=5)

        self.discover_button = ttk.Button(self.discover_frame, text="Discover", command=self.discover_gpus)
        self.discover_button.pack(side="left", padx=10, pady=5)

        self.gpu_listbox = tk.Listbox(self.discover_frame, height=5)
        self.gpu_listbox.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        # Section for submitting tasks
        self.submit_frame = ttk.LabelFrame(self, text="Submit Task")
        self.submit_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.submit_frame, text="Task Data URL:").pack(side="left", padx=5, pady=5)
        self.task_data_url = ttk.Entry(self.submit_frame)
        self.task_data_url.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.submit_task_button = ttk.Button(self.submit_frame, text="Submit Task", command=self.submit_task)
        self.submit_task_button.pack(side="left", padx=10, pady=5)

        # Section for task status
        self.status_frame = ttk.LabelFrame(self, text="Task Status")
        self.status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.status_text = scrolledtext.ScrolledText(self.status_frame)
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

    def on_discover_gpus_clicked(self):
        try:
            available_gpus = discover_gpus()
            self.gpu_listbox.delete(0, tk.END)  # Clear existing entries
            for gpu_name, status in available_gpus:
                self.gpu_listbox.insert(tk.END, f"{gpu_name} - {status}")
        except Exception as e:
            messagebox.showerror("Discovery Error", f"Failed to discover GPUs: {e}")
        else:
            messagebox.showinfo("Discovery", "GPU discovery completed successfully.")

    def on_submit_task_clicked(self):
        task_data_url = self.task_data_url.get()  # 예: 사용자가 입력한 데이터 URL을 가져옴
        provider_address = "0x..."  # 선택된 GPU 제공자의 주소
        try:
            training_request = {
                "taskDataUrl": task_data_url,
                # 필요한 추가 정보
            }
            receipt = submit_training_job(training_request, provider_address)
            print("작업 제출 성공:", receipt.transactionHash.hex())
        except Exception as e:
            print(f"작업 제출 중 오류 발생: {e}")

    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
