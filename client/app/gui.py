import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from utils import list_gpu, update_gpu_specs
import grpc 
import tasks_pb2
import tasks_pb2_grpc

class ApplicationGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.master.title("Distributed GPU Training Management")

        # Section to list GPUs,  Speces, Prices, and Address
        self.list_frame = ttk.LabelFrame(self, text="Update My GPU Specs and Price")
        self.list_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.list_frame, text="GPU Specs:").pack(side="left", padx=5, pady=5)
        self.specs_entry = ttk.Entry(self.list_frame)
        self.specs_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(self.list_frame, text="Price per Compute Unit:").pack(side="left", padx=5, pady=5)
        self.price_entry = ttk.Entry(self.list_frame)
        self.price_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(self.list_frame, text="Address:").pack(side="left", padx=5, pady=5)
        self.address_entry = ttk.Entry(self.list_frame)
        self.address_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.list_button = ttk.Button(self.list_frame, text="List GPU", command=self.update_gpu_specs)
        self.list_button.pack(side="right", padx=10, pady=5)

        # Modify the listing area to include a multi-selection listbox for GPUs
        self.list_frame = ttk.LabelFrame(self, text="Available GPUs")
        self.list_frame.pack(fill="x", padx=10, pady=5)
        self.gpu_listbox = tk.Listbox(self.list_frame, selectmode='multiple', height=6)  # Allow multi-selection
        self.gpu_listbox.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.refresh_button = ttk.Button(self.list_frame, text="Refresh GPU List", command=self.list_gpu)
        self.refresh_button.pack(side="right", padx=10, pady=5)

        # Status display
        self.status_frame = ttk.LabelFrame(self, text="Status")
        self.status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.status_text = scrolledtext.ScrolledText(self.status_frame)
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Controls for updating training sessions
        self.update_frame = ttk.LabelFrame(self, text="Update Training Session")
        self.update_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.update_frame, text="Session ID:").pack(side="left", padx=5, pady=5)
        self.session_id_entry = ttk.Entry(self.update_frame)
        self.session_id_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ttk.Label(self.update_frame, text="Epoch:").pack(side="left", padx=5, pady=5)
        self.epoch_entry = ttk.Entry(self.update_frame)
        self.epoch_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Label for device only cuda
        ttk.Label(self.update_frame, text="Device:").pack(side="left", padx=5, pady=5)
        self.device_entry = ttk.Entry(self.update_frame)
        self.device_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.send_button = tk.Button(self, text="Start Training Session", command=self.start_training_session)
        self.send_button.pack(side="top")
        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit_button.pack(side="bottom")

       # grpc and rent gpus 
    def rent_gpu(self):

        # Rent GPU with the selected parameters
        selected_indices = self.gpu_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a GPU to rent.")
            return
        
        selected_gpus = [self.gpu_list[int(i)] for i in selected_indices]  # 이전에 gpu_list에 gpu 정보가 저장되어 있다고 가정
        for gpu in selected_gpus:
            gpu_id = gpu['id']
            address = gpu['address']
            compute_units = int(self.compute_units_entry.get())
            channel = grpc.insecure_channel(address)
            stub = tasks_pb2_grpc.TaskServiceStub(channel)
            response = stub.RentGPU(tasks_pb2.RentGPURequest(gpu_id=gpu_id, compute_units=compute_units))
            status = response.status
            self.update_status(f"Rented GPU {gpu_id} with {compute_units} compute units. Status: {status}.")


    # start training session to selecteds address by grpc
    def start_training_session(self):
        selected_indices = self.gpu_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a GPU to start the training session.")
            return
        
        selected_gpus = [self.gpu_list[int(i)] for i in selected_indices]  # 이전에 gpu_list에 gpu 정보가 저장되어 있다고 가정

        filename = filedialog.askopenfilename()  # Choose the file to send
        if not filename:
            messagebox.showerror("Error", "No dataset file selected.")
            return

        with open(filename, 'rb') as f:
            dataset = f.read()

        # 데이터셋 분할
        total_gpus = len(selected_gpus)
        chunk_size = len(dataset) // total_gpus
        dataset_chunks = [dataset[i * chunk_size:(i + 1) * chunk_size] for i in range(total_gpus)]
        if len(dataset) % total_gpus:
            dataset_chunks[-1] += dataset[-(len(dataset) % total_gpus):]

        # 각 GPU에 데이터셋 조각 전송
        for gpu, data_chunk in zip(selected_gpus, dataset_chunks):
            gpu_id = gpu['id']
            model = self.model_entry.get()
            epoch = int(self.epoch_entry.get())
            device = self.device_entry.get()
            parameters = tasks_pb2.ModelParameters(epoch=epoch, device=device)
            address = gpu['address']  # 각 GPU의 주소 사용
            channel = grpc.insecure_channel(address)
            stub = tasks_pb2_grpc.TaskServiceStub(channel)

            response = stub.StartTrainingSession(tasks_pb2.StartTrainingSessionRequest(
                gpu_id=gpu_id, model_data=tasks_pb2.ModelData(model=model, dataset=data_chunk, parameters=parameters)
            ))
            if response.status != "success":
                messagebox.showerror("Error", f"Failed to send model data to GPU {gpu_id}")
            else:
                messagebox.showinfo("Success", f"Model data sent successfully to GPU {gpu_id}!")



    # List gpu with specs and price and address
    def list_gpu(self):
        self.gpu_listbox.delete(0, tk.END)
        gpus = list_gpu()
        for gpu in gpus:
            self.gpu_listbox.insert(tk.END, f"{gpu['gpu_id']} - {gpu['specs']} - {gpu['price']} - {gpu['address']}")

    # Register My GPU Specs and Price
    def update_gpu_specs(self):
        specs = self.specs_entry.get()
        price = self.price_entry.get()
        address = self.address_entry.get()
        if specs and price and address:
            update_gpu_specs(address, specs, price)
            self.update_status(f"Updated GPU specs to {specs} and price to {price}.")
            

    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationGUI(master=root)
    app.mainloop()
