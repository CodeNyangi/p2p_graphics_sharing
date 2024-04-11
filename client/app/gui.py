import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from utils import list_gpu, rent_gpu, start_training_session, update_training, change_aggregator

class ApplicationGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.master.title("Distributed GPU Training Management")

        # Section to list GPUs
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

    def create_training_controls(self):
        # Controls for updating training sessions
        self.update_frame = ttk.LabelFrame(self, text="Update Training Session")
        self.update_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.update_frame, text="Session ID:").pack(side="left", padx=5, pady=5)
        self.session_id_entry = ttk.Entry(self.update_frame)
        self.session_id_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ttk.Label(self.update_frame, text="Epoch:").pack(side="left", padx=5, pady=5)
        self.epoch_entry = ttk.Entry(self.update_frame)
        self.epoch_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ttk.Label(self.update_frame, text="Parameter Hash:").pack(side="left", padx=5, pady=5)
        self.param_hash_entry = ttk.Entry(self.update_frame)
        self.param_hash_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.update_button = ttk.Button(self.update_frame, text="Update Training", command=self.update_training)
        self.update_button.pack(side="right", padx=10, pady=5)

        # Controls for changing the aggregator
        self.change_agg_frame = ttk.LabelFrame(self, text="Change Aggregator")
        self.change_agg_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.change_agg_frame, text="New Aggregator Address:").pack(side="left", padx=5, pady=5)
        self.new_agg_entry = ttk.Entry(self.change_agg_frame)
        self.new_agg_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.change_agg_button = ttk.Button(self.change_agg_frame, text="Change Aggregator", command=self.change_aggregator)
        self.change_agg_button.pack(side="right", padx=10, pady=5)

    def update_training(self):
        session_id = int(self.session_id_entry.get())
        epoch = int(self.epoch_entry.get())
        parameter_hash = self.param_hash_entry.get()
        update_training(session_id, epoch, parameter_hash)
        self.update_status(f"Updated training for session {session_id} to epoch {epoch}.")

    def change_aggregator(self):
        session_id = int(self.session_id_entry.get())
        new_aggregator = self.new_agg_entry.get()
        change_aggregator(session_id, new_aggregator)
        self.update_status(f"Changed aggregator for session {session_id} to {new_aggregator}.")

    def list_gpu(self):
        specs = self.specs_entry.get()
        price_per_compute_unit = float(self.price_entry.get())
        list_gpu(specs, price_per_compute_unit)
        self.update_status(f"GPU listed with specs: {specs} at {price_per_compute_unit} per unit.")

    def rent_gpu(self):
        gpu_id = int(self.gpu_id_entry.get())
        compute_units = int(self.compute_units_entry.get())
        model = self.model_entry.get()
        dataset = self.dataset_entry.get()
        rent_gpu(gpu_id, compute_units, model, dataset)
        self.update_status(f"GPU {gpu_id} rented for model {model} with dataset {dataset} using {compute_units} compute units.")

    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationGUI(master=root)
    app.mainloop()
