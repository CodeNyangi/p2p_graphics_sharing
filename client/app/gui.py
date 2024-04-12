import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from utils import list_gpu
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
        self.list_frame = ttk.LabelFrame(self, text="List a New GPU")
        self.list_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.list_frame, text="Specs:").pack(side="left", padx=5, pady=5)
        self.specs_entry = ttk.Entry(self.list_frame)
        self.specs_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ttk.Label(self.list_frame, text="Price Per Compute Unit:").pack(side="left", padx=5, pady=5)
        self.price_entry = ttk.Entry(self.list_frame)
        self.price_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.list_button = ttk.Button(self.list_frame, text="List GPU", command=self.list_gpu)
        self.list_button.pack(side="right", padx=10, pady=5)

        ttk.Label(self.list_frame, text="Address:").pack(side="left", padx=5, pady=5)
        self.address_entry = ttk.Entry(self.list_frame)
        self.address_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Section to rent GPUs
        self.rent_frame = ttk.LabelFrame(self, text="Rent GPU")
        self.rent_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.rent_frame, text="GPU ID:").pack(side="left", padx=5, pady=5)
        self.gpu_id_entry = ttk.Entry(self.rent_frame)
        self.gpu_id_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(self.rent_frame, text="Compute Units:").pack(side="left", padx=5, pady=5)
        self.compute_units_entry = ttk.Entry(self.rent_frame)
        self.compute_units_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(self.rent_frame, text="Model:").pack(side="left", padx=5, pady=5)
        self.model_entry = ttk.Entry(self.rent_frame)
        self.model_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(self.rent_frame, text="Dataset:").pack(side="left", padx=5, pady=5)
        self.dataset_entry = ttk.Entry(self.rent_frame)
        self.dataset_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.rent_button = ttk.Button(self.rent_frame, text="Rent GPU", command=self.rent_gpu)
        self.rent_button.pack(side="right", padx=10, pady=5)

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

        self.send_button = tk.Button(self, text="Send Dataset", command=self.start_training_session)
        self.send_button.pack(side="top")
        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit_button.pack(side="bottom")

       # grpc and rent gpus 
    def rent_gpu(self):
        gpu_id = self.gpu_id_entry.get()
        address = self.address_entry.get()
        compute_units = int(self.compute_units_entry.get())

        # Call the rent_gpu function from grpc with the selected parameters
        channel = grpc.insecure_channel(address)
        stub = tasks_pb2_grpc.TaskServiceStub(channel)
        response = stub.RentGPU(tasks_pb2.RentGPURequest(gpu_id=gpu_id, compute_units=compute_units))
        status = response.status
        # Update the status display
        self.update_status(f"Rented GPU {gpu_id} with {compute_units} compute units. Status: {status}.")

    # Send model data to selected and rent gpu address by grpc
    def start_training_session(self):
        gpu_id = self.gpu_id_entry.get()
        model = self.model_entry.get()
        epoch = int(self.epoch_entry.get())
        device = self.device_entry.get()
        parameters = tasks_pb2.ModelParameters(epoch=epoch, device=device)
        filename = filedialog.askopenfilename()  # Choose the file to send
        address = self.address_entry.get()
        if filename:
            with open(filename, 'rb') as f:
                dataset = f.read()

            channel = grpc.insecure_channel(address)
            stub = tasks_pb2_grpc.TaskServiceStub(channel)

            response = stub.StartTrainingSession(tasks_pb2.StartTrainingSessionRequest( gpu_id=gpu_id, model_data = tasks_pb2.ModelData(model=model, dataset=dataset, parameters=parameters)))
            if response.status == "success":
                messagebox.showinfo("Success", "Model data sent successfully!")
            else:
                messagebox.showerror("Error", "Failed to send model data.")

    # List gpu with specs and price and address
    def list_gpu(self):
        specs = self.specs_entry.get()
        price_per_compute_unit = float(self.price_entry.get())
        list_gpu(specs, price_per_compute_unit)

        # Update the status display
        self.update_status(f"GPU listed with specs: {specs} at {price_per_compute_unit} per unit.")

    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationGUI(master=root)
    app.mainloop()
