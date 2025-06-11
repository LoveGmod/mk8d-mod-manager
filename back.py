import requests
import zipfile
import os
import shutil
from io import BytesIO
import tempfile
import json

MODS_DB_PATH = os.path.join(os.getenv("APPDATA"), "LG MK8D Mod Manager", "installed_mods.json")

def load_installed_mods():
    if os.path.exists(MODS_DB_PATH):
        with open(MODS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_installed_mod(repo, version):
    os.makedirs(os.path.dirname(MODS_DB_PATH), exist_ok=True)
    mods = load_installed_mods()
    mods[repo] = {"version": version}
    with open(MODS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=4)

def get_latest_release_info(repo):
    api_url = f"https://api.github.com/repos/LoveGmod/{repo}/releases/latest"
    r = requests.get(api_url)
    r.raise_for_status()
    return r.json()

def get_latest_release_zip_url(repo):
    release_info = get_latest_release_info(repo)
    for asset in release_info["assets"]:
        if asset["name"].endswith(".zip"):
            return asset["browser_download_url"], release_info["tag_name"]
    raise Exception("Aucun fichier .zip trouvé dans la dernière release.")

def remove_installed_mod(repo):
    mods = load_installed_mods()
    if repo in mods:
        del mods[repo]
        os.makedirs(os.path.dirname(MODS_DB_PATH), exist_ok=True)
        with open(MODS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(mods, f, indent=4)

def uninstall_mod_files():
    install_path = os.path.join(os.getenv("APPDATA"), "Ryujinx/mods/contents/0100152000022000")
    if os.path.exists(install_path):
        shutil.rmtree(install_path)
        return True
    return False

def install_mod(repo, progress_callback=None):
    def update_progress(value):
        if progress_callback:
            progress_callback(value)

    update_progress(5)

    install_path = os.path.join(os.getenv("APPDATA"), "Ryujinx/mods/contents/0100152000022000")

    if os.path.exists(install_path) and any(os.scandir(install_path)):
        update_progress(10)
        print("Le mod est déjà installé, mise à jour en cours")
        shutil.rmtree(install_path)

    update_progress(20)

    print(f"Téléchargement du mod depuis LoveGmod/{repo}")
    zip_url, version = get_latest_release_zip_url(repo)
    update_progress(25)

    response = requests.get(zip_url)
    response.raise_for_status()
    update_progress(40)

    print("Extraction")
    temp_folder = os.path.join(tempfile.gettempdir(), "temp_mod")
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(temp_folder)
    update_progress(60)

    print("Installation")
    os.makedirs(install_path, exist_ok=True)

    for item in os.listdir(temp_folder):
        s = os.path.join(temp_folder, item)
        d = os.path.join(install_path, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy(s, d)

    update_progress(90)

    print("Mod installé avec succès")
    save_installed_mod(repo, version)
    shutil.rmtree(temp_folder, ignore_errors=True)
    update_progress(100)