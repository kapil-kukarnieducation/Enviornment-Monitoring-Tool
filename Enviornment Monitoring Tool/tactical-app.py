import tkinter as tk
import urllib.request
import json
import threading
import time

TASMOTA_IP = "192.168.1.11"

class CyberTacticalHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("TAC-SOC // SHT4X CYBER MONITOR [LIGHT HUD]")
        self.geometry("640x480")
        self.configure(bg="#f1f5f9")  # Light tactical slate-white background
        self.resizable(False, False)

        # Cyber-Tactical Light Theme Color Palette
        self.COLOR_BG = "#f1f5f9"
        self.COLOR_PANEL = "#ffffff"
        self.COLOR_BORDER = "#cbd5e1"
        self.COLOR_ACCENT = "#0284c7"  # Cyber Blue
        self.COLOR_TEXT = "#0f172a"    # Deep Slate / Dark Text
        self.COLOR_DIM = "#64748b"     # Muted Label Text
        self.COLOR_AMBER = "#d97706"
        self.COLOR_RED = "#dc2626"

        # Fonts
        self.FONT_TITLE = ("Consolas", 12, "bold")
        self.FONT_HEADER = ("Consolas", 9, "bold")
        self.FONT_VALUE = ("Consolas", 22, "bold")
        self.FONT_LABEL = ("Consolas", 8, "bold")
        self.FONT_MONO = ("Consolas", 8)

        self.create_widgets()
        self.running = True
        
        # Start background polling thread
        self.poll_thread = threading.Thread(target=self.background_poller, daemon=True)
        self.poll_thread.start()

    def create_widgets(self):
        # Top Cyber Header Bar
        header_frame = tk.Frame(self, bg=self.COLOR_PANEL, bd=1, relief="solid", highlightbackground=self.COLOR_ACCENT)
        header_frame.pack(fill="x", padx=10, pady=10)

        lbl_title = tk.Label(header_frame, text="[SOC-MONITOR] // SHT4X TELEMETRY STREAM", font=self.FONT_TITLE, bg=self.COLOR_PANEL, fg=self.COLOR_ACCENT)
        lbl_title.pack(side="left", padx=10, pady=8)

        self.lbl_status = tk.Label(header_frame, text="INITIATING SOCKET...", font=self.FONT_HEADER, bg=self.COLOR_PANEL, fg=self.COLOR_AMBER)
        self.lbl_status.pack(side="right", padx=10, pady=8)

        # Metrics Display Grid
        grid_frame = tk.Frame(self, bg=self.COLOR_BG)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=0)

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        # Metric Cards
        self.card_temp = self.make_metric_card(grid_frame, "SHT4X TEMPERATURE", "0.0", "°C", 0, 0)
        self.card_hum = self.make_metric_card(grid_frame, "SHT4X HUMIDITY", "0.0", "%", 0, 1)
        self.card_dew = self.make_metric_card(grid_frame, "SHT4X DEW POINT", "0.0", "°C", 1, 0)
        self.card_aqi = self.make_metric_card(grid_frame, "AIR QUALITY INDEX (AQI)", "42", "AQI", 1, 1)

        # Threshold Boundary Controls Frame
        ctrl_frame = tk.Frame(self, bg=self.COLOR_PANEL, bd=1, relief="solid", highlightbackground=self.COLOR_BORDER)
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(ctrl_frame, text="THRESHOLD ALERT BOUNDARIES", font=self.FONT_HEADER, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack(anchor="w", padx=10, pady=(6, 2))

        inputs_sub = tk.Frame(ctrl_frame, bg=self.COLOR_PANEL)
        inputs_sub.pack(fill="x", padx=10, pady=(0, 6))

        # Temp Threshold Input
        tk.Label(inputs_sub, text="Max Temp (°C):", font=self.FONT_LABEL, bg=self.COLOR_PANEL, fg=self.COLOR_DIM).grid(row=0, column=0, sticky="w", padx=5)
        self.ent_temp_max = tk.Entry(inputs_sub, font=self.FONT_MONO, width=6, bg="#f8fafc", fg=self.COLOR_TEXT, bd=1, relief="solid")
        self.ent_temp_max.insert(0, "38.0")
        self.ent_temp_max.grid(row=0, column=1, padx=5)

        # Humidity Threshold Input
        tk.Label(inputs_sub, text="Max Humidity (%):", font=self.FONT_LABEL, bg=self.COLOR_PANEL, fg=self.COLOR_DIM).grid(row=0, column=2, sticky="w", padx=5)
        self.ent_hum_max = tk.Entry(inputs_sub, font=self.FONT_MONO, width=6, bg="#f8fafc", fg=self.COLOR_TEXT, bd=1, relief="solid")
        self.ent_hum_max.insert(0, "70.0")
        self.ent_hum_max.grid(row=0, column=3, padx=5)

        # Live Packet Inspector Log Box (Terminal Style)
        log_frame = tk.Frame(self, bg=self.COLOR_PANEL, bd=1, relief="solid", highlightbackground=self.COLOR_BORDER)
        log_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(log_frame, text="RAW PACKET INSPECTOR // 192.168.1.11", font=("Consolas", 7, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_DIM).pack(anchor="w", padx=8, pady=(4, 0))
        
        self.txt_log = tk.Text(log_frame, height=4, bg="#0f172a", fg="#38bdf8", font=("Consolas", 8), bd=0, padx=5, pady=5)
        self.txt_log.pack(fill="x", padx=8, pady=6)
        self.txt_log.insert("1.0", "Awaiting telemetry stream...")

    def make_metric_card(self, parent, title, val, unit, r, c):
        card = tk.Frame(parent, bg=self.COLOR_PANEL, bd=1, relief="solid", highlightbackground=self.COLOR_BORDER, width=300, height=95)
        card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        card.grid_propagate(False)

        tk.Label(card, text=title, font=self.FONT_LABEL, bg=self.COLOR_PANEL, fg=self.COLOR_DIM).pack(anchor="w", padx=10, pady=(8, 0))
        
        val_frame = tk.Frame(card, bg=self.COLOR_PANEL)
        val_frame.pack(anchor="w", padx=10, pady=2)

        lbl_val = tk.Label(val_frame, text=val, font=self.FONT_VALUE, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT)
        lbl_val.pack(side="left")

        lbl_unit = tk.Label(val_frame, text=unit, font=("Consolas", 10, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_ACCENT)
        lbl_unit.pack(side="left", padx=5, pady=(6, 0))

        card.lbl_val = lbl_val
        return card

    def background_poller(self):
        while self.running:
            try:
                url = f"http://{TASMOTA_IP}/cm?cmnd=Status%2010"
                req = urllib.request.Request(url, headers={'User-Agent': 'CyberTacticalClient/1.0'})
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = json.loads(response.read().decode())
                    self.after(0, lambda: self.update_telemetry(data, None))
            except Exception as e:
                self.after(0, lambda err=str(e): self.update_telemetry(None, err))
            
            time.sleep(5)

    def update_telemetry(self, data, error):
        if error:
            self.lbl_status.config(text="CONNECTION FAILED", fg=self.COLOR_RED)
            self.txt_log.delete("1.0", tk.END)
            self.txt_log.insert("1.0", f"ERROR: {error}\nTarget {TASMOTA_IP} unreachable.")
            return

        self.lbl_status.config(text="ONLINE // LIVE SEC-STREAM", fg=self.COLOR_ACCENT)
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.insert("1.0", json.dumps(data, indent=2))

        # Parse JSON keys safely
        sns = data.get("StatusSNS", data)
        sensor = sns.get("SHT4X", sns.get("SHT3X", sns))

        temp = sensor.get("Temperature", sensor.get("Temp", 33.6))
        hum = sensor.get("Humidity", sensor.get("Hum", 39.6))
        dew = sensor.get("DewPoint", sensor.get("Dew_point", 18.0))

        # Update Card Values
        self.card_temp.lbl_val.config(text=f"{float(temp):.1f}")
        self.card_hum.lbl_val.config(text=f"{float(hum):.1f}")
        self.card_dew.lbl_val.config(text=f"{float(dew):.1f}")

        # Threshold Breach Alert Indicators
        try:
            max_t = float(self.ent_temp_max.get())
            max_h = float(self.ent_hum_max.get())
            
            if float(temp) > max_t:
                self.card_temp.config(highlightbackground=self.COLOR_RED, bd=2)
            else:
                self.card_temp.config(highlightbackground=self.COLOR_BORDER, bd=1)

            if float(hum) > max_h:
                self.card_hum.config(highlightbackground=self.COLOR_RED, bd=2)
            else:
                self.card_hum.config(highlightbackground=self.COLOR_BORDER, bd=1)
        except ValueError:
            pass

    def destroy(self):
        self.running = False
        super().destroy()

if __name__ == "__main__":
    app = CyberTacticalHUD()
    app.mainloop()