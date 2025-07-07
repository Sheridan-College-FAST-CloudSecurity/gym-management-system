from gym_manager.gui.app import GymManagerApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = GymManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()