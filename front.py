import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import requests

from back import install_mod

class ModInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mod Installer - Mario Kart 8 Deluxe")
        self.geometry("500x400")
        self.resizable(False, False)

        self.mods = self.load_mods()
        self.create_widgets()

    def load_mods(self):
        try:
            r = requests.get("https://raw.githubusercontent.com/LoveGmod/mk8d-mod-manager/main/mods.json")
            r.raise_for_status()
            data = r.json()
            return data["mods"]
        except Exception as e:
            messagebox.showerror("Erreur de chargement", f"Impossible de charger la liste des mods :\n{e}")
            self.quit()

    def create_widgets(self):
        title = tk.Label(self, text="Sélectionnez un mod à installer :", font=("Helvetica", 14))
        title.pack(pady=10)

        self.listbox = tk.Listbox(self, font=("Helvetica", 12), height=10)
        for mod in self.mods:
            self.listbox.insert(tk.END, mod["name"])
        self.listbox.pack(padx=20, fill="x")

        self.install_button = tk.Button(self, text="Installer le mod sélectionné", command=self.install_selected_mod)
        self.install_button.pack(pady=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

    def install_selected_mod(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucun mod sélectionné", "Veuillez sélectionner un mod à installer.")
            return

        mod = self.mods[selected[0]]
        self.install_button.config(state="disabled")
        self.progress["value"] = 0

        thread = threading.Thread(target=self.install_mod_thread, args=(mod,))
        thread.start()

    def update_progress(self, value):
        self.progress["value"] = value
        self.update_idletasks()

    def install_mod_thread(self, mod):
        try:
            install_mod(mod["repo"], self.update_progress)
            messagebox.showinfo("Succès", f"{mod['name']} installé avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            self.install_button.config(state="normal")
            self.progress["value"] = 0


if __name__ == "__main__":
    app = ModInstallerApp()
    app.mainloop()
