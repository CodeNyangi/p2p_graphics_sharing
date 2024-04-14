import tensorflow as tf
from tensorflow import distribute
from transformers import TFAutoModel, AutoConfig
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from utils import list_gpu, update_gpu_specs
import grpc 
import pickle
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

        # Dropdown for selecting the learning strategy
        self.strategy_var = tk.StringVar()
        self.strategy_label = ttk.Label(root, text="Select Learning Strategy:")
        self.strategy_label.pack(fill='x', padx=5, pady=5)
        self.strategy_dropdown = ttk.Combobox(root, textvariable=self.strategy_var)
        self.strategy_dropdown['values'] = ("Mirrored", "One Device")
        self.strategy_dropdown.pack(fill='x', padx=5, pady=5)
        # self.strategy_dropdown.bind("<<ComboboxSelected>>", self.on_strategy_change)

        # Dropdown for selecting the training method
        self.training_var = tk.StringVar()
        self.training_label = ttk.Label(root, text="Select Training Method:")
        self.training_label.pack(fill='x', padx=5, pady=5)
        self.training_dropdown = ttk.Combobox(root, textvariable=self.training_var)
        self.training_dropdown['values'] = ("Fine-tune", "Transfer Learning")
        self.training_dropdown.pack(fill='x', padx=5, pady=5)
        # self.training_dropdown.bind("<<ComboboxSelected>>", self.on_training_change)

        # Load Model Entry
        ttk.Label(self, text="Model Path:").pack(side="left", padx=5, pady=5)
        self.model_entry = ttk.Entry(self)
        self.model_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Model Strategy Entry
        ttk.Label(self, text="Compute Units:").pack(side="left", padx=5, pady=5)
        self.model_strategy_entry = ttk.Entry(self)
        self.model_strategy_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Controls for updating training sessions
        self.update_frame = ttk.LabelFrame(self, text="Update Training Session")
        self.update_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.update_frame, text="Session ID:").pack(side="left", padx=5, pady=5)
        self.session_id_entry = ttk.Entry(self.update_frame)
        self.session_id_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ttk.Label(self.update_frame, text="Epoch:").pack(side="left", padx=5, pady=5)
        self.epoch_entry = ttk.Entry(self.update_frame)
        self.epoch_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Label for device
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
            compute_units = gpu['compute_units']
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
        
        selected_gpus = [self.gpu_list[int(i)] for i in selected_indices]

        filename = filedialog.askopenfilename()  # Choose the file to send
        if not filename:
            messagebox.showerror("Error", "No dataset file selected.")
            return

        with open(filename, 'rb') as f:
            dataset = f.read()

        # Assume the following attributes are set elsewhere in the GUI:
        strategy_type = self.strategy_var.get()  # "Mirrored" or "One Device"
        training_type = self.training_var.get()  # "Fine-tune" or "Transfer Learning"

        if strategy_type == "Mirrored":
            # Using TensorFlow MirroredStrategy
            strategy = distribute.MirroredStrategy(devices=[f"/gpu:{gpu['id'][-1]}" for gpu in selected_gpus])
        elif strategy_type == "One Device":
            # Using TensorFlow's simple device placement
            strategy = tf.device(f"/gpu:{selected_gpus[0]['id'][-1]}")

        with strategy.scope():
            model = self.load_model()  # You'd need to define how to load your model based on the training type

            # If using MirroredStrategy, TensorFlow handles data distribution internally
            dataset_chunks = self.split_dataset(dataset, len(selected_gpus))

            for gpu, data_chunk in zip(selected_gpus, dataset_chunks):
                self.send_model_data_to_gpu(gpu, model, data_chunk)

    def load_model(self):
        # Assume self.model_entry.get() returns the model ID from Hugging Face
        model_id = self.model_entry.get()

        # Load the model configuration from Hugging Face
        config = AutoConfig.from_pretrained(model_id)

        # Load the model from Hugging Face
        # If the model is a standard classification model, use TFAutoModelForSequenceClassification
        # Adjust according to the specific type of model you are dealing with
        model = TFAutoModel.from_pretrained(model_id, config=config)

        return model
        

    def split_dataset(self, dataset, num_parts):
        chunk_size = len(dataset) // num_parts
        return [dataset[i * chunk_size:(i + 1) * chunk_size] for i in range(num_parts)]

    def serialize_model(model):
    # Serialize only the weights and model configuration
        model_weights = model.get_weights()  # Get model weights as a list of numpy arrays
        model_config = model.get_config()  # Get model configuration as a dictionary
        
        # Use pickle to serialize the model weights and config
        serialized_model = pickle.dumps((model_config, model_weights))
        return serialized_model

    def serialize_data(data):
        # Use pickle to serialize dataset
        serialized_data = pickle.dumps(data)
        return serialized_data

    def send_model_data_to_gpu(self, gpu, model, dataset_chunk):
        serialized_model = self.serialize_model(model)
        serialized_data = self.serialize_data(dataset_chunk)

        # Now send serialized data via gRPC
        gpu_id = gpu['id']
        address = gpu['address']
        epoch = int(self.epoch_entry.get())  # Assuming this retrieves an integer epoch count
        channel = grpc.insecure_channel(address)
        stub = tasks_pb2_grpc.TaskServiceStub(channel)

        response = stub.StartTrainingSession(tasks_pb2.StartTrainingSessionRequest(
            gpu_id=gpu_id,
            model_data=serialized_model,
            dataset=serialized_data,
            hyperparameters=tasks_pb2.ModelParameters(epoch=epoch, device=self.device_entry.get(), strategy=self.strategy_var.get(), training=self.training_var.get())
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
