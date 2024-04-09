import tkinter as tk
from tkinter import messagebox
from client.app.gui import ApplicationGUI  # Ensure this path matches your project structure

def main():
    try:
        # Initialize the main window
        root = tk.Tk()
        root.title('Distributed GPU Cloud Networks Client')

        # Setup the window size or make it adjustable according to your needs
        root.geometry('800x600')  # Example window size

        # Initialize and place the GUI application
        app = ApplicationGUI(master=root)
        app.mainloop()

    except Exception as e:
        messagebox.showerror("Initialization Error", f"Failed to start the application: {e}")
        print(f"Error starting the application: {e}")

if __name__ == '__main__':
    main()
