import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
import platform
from plyer import notification

# Küszöbértékek
DOWNLOAD_THRESHOLD = 5  # Mbps
UPLOAD_THRESHOLD = 2    # Mbps
PING_HOST = "8.8.8.8"  # Google DNS, pinghez
CHECK_INTERVAL = 1      # másodpercenként ellenőrzés

class NetworkMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hálózatfigyelő")
        self.geometry("400x200")
        self.resizable(False, False)

        self.download_speed_var = tk.StringVar(value="Letöltés: -- Mbps")
        self.upload_speed_var = tk.StringVar(value="Feltöltés: -- Mbps")
        self.status_var = tk.StringVar(value="Állapot: Ellenőrzés...")

        # GUI elemek
        ttk.Label(self, textvariable=self.download_speed_var, font=("Arial", 12)).pack(pady=10)
        ttk.Label(self, textvariable=self.upload_speed_var, font=("Arial", 12)).pack(pady=10)
        ttk.Label(self, textvariable=self.status_var, font=("Arial", 12)).pack(pady=10)

        # Indítjuk a háttér szálat
        threading.Thread(target=self.monitor_network, daemon=True).start()

    def ping_test(self, host):
        """Ping teszt a gyors real-time ellenőrzéshez"""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        try:
            output = subprocess.check_output(["ping", param, "1", host], stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    def monitor_network(self):
        import speedtest
        st = speedtest.Speedtest()
        while True:
            connected = self.ping_test(PING_HOST)
            if connected:
                try:
                    # Mérjük a sebességet (ez kicsit lassabb, ~5-10 mp)
                    download = st.download() / 1_000_000
                    upload = st.upload() / 1_000_000
                    self.download_speed_var.set(f"Letöltés: {download:.2f} Mbps")
                    self.upload_speed_var.set(f"Feltöltés: {upload:.2f} Mbps")
                    self.status_var.set("Állapot: Kapcsolat él")

                    # Küszöbérték ellenőrzés
                    if download < DOWNLOAD_THRESHOLD or upload < UPLOAD_THRESHOLD:
                        notification.notify(
                            title="Hálózati figyelmeztetés",
                            message=f"Hálózat lassú!\nLetöltés: {download:.2f} Mbps\nFeltöltés: {upload:.2f} Mbps",
                            timeout=5
                        )

                except Exception as e:
                    self.status_var.set("Állapot: Hiba a sebességmérésnél")
                    notification.notify(
                        title="Hálózati hiba",
                        message=f"Hiba a mérés közben: {e}",
                        timeout=5
                    )
            else:
                self.status_var.set("Állapot: Nincs kapcsolat!")
                notification.notify(
                    title="Hálózati figyelmeztetés",
                    message="A hálózat megszakadt!",
                    timeout=5
                )
                self.download_speed_var.set("Letöltés: -- Mbps")
                self.upload_speed_var.set("Feltöltés: -- Mbps")

            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    app = NetworkMonitor()
    app.mainloop()
