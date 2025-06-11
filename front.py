import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import requests
import webbrowser
import subprocess
import tempfile
import os

from back import install_mod

CURRENT_VERSION = "1.1.0"

class ModInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mod Installer - Mario Kart 8 Deluxe")
        self.geometry("500x400")
        self.resizable(False, False)

        self.mods = self.load_mods()
        self.create_widgets()

        self.after(1000, self.check_for_updates)

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

    def check_for_updates(self):
        try:
             url = f"https://api.github.com/repos/LoveGmod/mk8d-mod-manager/releases/latest"
             
             r = requests.get(url)
             r.raise_for_status()

             latest = r.json()
             latest_version = latest["tag_name"].lstrip("v")

             if latest_version != CURRENT_VERSION:
                 if "[force-update]" in latest.get("body", "").lower():
                    messagebox.showinfo("Mise à jour obligatoire", f"La version {latest_version} est obligatoire.\nElle va être installée maintenant.")
                    self.download_and_install(latest)
                 else:
                    if messagebox.askyesno(
                     "Mise à jour disponible",
                     f"Une nouvelle version ({latest_version}) est disponible.\nSouhaitez-vous la télécharger ?"
                 ):
                     self.download_and_install(latest)
        except Exception as e:
            print(f"Erreur vérification mise à jour : {e}")

    def download_and_install(self, release_data):
        try:
            assets = release_data.get("assets", [])
            installer_asset = next((a for a in assets if a["name"].endswith(".exe")), None)

            if not installer_asset:
                messagebox.showerror("Erreur", "Aucun installateur trouvé dans la release.")
                return
            
            url = installer_asset["browser_download_url"]

            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, installer_asset["name"])
            with open(installer_path, "wb") as f:
                r = requests.get(url, stream=True)
                r.raise_for_status()
                
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            subprocess.Popen([installer_path])

            self.quit()
        except Exception as e:
            messagebox.showerror("Erreur mise à jour", f"Impossible d'installer la mise à jour :\n{e}")




if __name__ == "__main__":
    app = ModInstallerApp()
    app.mainloop()
