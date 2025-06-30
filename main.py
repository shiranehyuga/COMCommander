
import customtkinter
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("COM Commander")
        self.geometry("1000x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.log_data = []
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None

        # --- Top Frame ---
        self.top_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.top_frame.grid_columnconfigure(7, weight=1)

        self.port_label = customtkinter.CTkLabel(self.top_frame, text="COM Port:")
        self.port_label.grid(row=0, column=0, padx=10, pady=10)
        self.port_menu = customtkinter.CTkOptionMenu(self.top_frame, values=self.get_available_ports())
        self.port_menu.grid(row=0, column=1, padx=10, pady=10)

        self.baud_label = customtkinter.CTkLabel(self.top_frame, text="Baud Rate:")
        self.baud_label.grid(row=0, column=2, padx=10, pady=10)
        self.baud_entry = customtkinter.CTkEntry(self.top_frame)
        self.baud_entry.grid(row=0, column=3, padx=10, pady=10)
        self.baud_entry.insert(0, "115200")

        self.connect_button = customtkinter.CTkButton(self.top_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=4, padx=10, pady=10)
        self.refresh_button = customtkinter.CTkButton(self.top_frame, text="Refresh", command=self.refresh_ports)
        self.refresh_button.grid(row=0, column=5, padx=10, pady=10)
        
        self.auto_scroll_var = customtkinter.BooleanVar(value=True)
        self.auto_scroll_checkbox = customtkinter.CTkCheckBox(self.top_frame, text="Auto Scroll", variable=self.auto_scroll_var)
        self.auto_scroll_checkbox.grid(row=0, column=6, padx=10, pady=10)

        # --- Data Display Frame ---
        self.display_frame = customtkinter.CTkScrollableFrame(self)
        self.display_frame.grid(row=1, column=0, padx=(10,0), pady=10, sticky="nsew")

        # --- Right Control Frame ---
        self.control_frame = customtkinter.CTkScrollableFrame(self)
        self.control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

        # --- Format Selection ---
        self.format_frame = customtkinter.CTkFrame(self.control_frame)
        self.format_frame.pack(pady=10, padx=10, fill="x")

        self.rx_display_format_var = customtkinter.StringVar(value="ASCII")
        self.tx_display_format_var = customtkinter.StringVar(value="ASCII")
        self.tx_display_format_var = customtkinter.StringVar(value="ASCII")
        self.tx_format_var = customtkinter.StringVar(value="ASCII")

        customtkinter.CTkLabel(self.format_frame, text="RX Display Format").pack(pady=5)
        customtkinter.CTkRadioButton(self.format_frame, text="ASCII", variable=self.rx_display_format_var, value="ASCII", command=self.redisplay_all_logs).pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="HEX", variable=self.rx_display_format_var, value="HEX", command=self.redisplay_all_logs).pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="BIN", variable=self.rx_display_format_var, value="BIN", command=self.redisplay_all_logs).pack(anchor="w", padx=10)

        customtkinter.CTkLabel(self.format_frame, text="TX Display Format").pack(pady=10)
        customtkinter.CTkRadioButton(self.format_frame, text="ASCII", variable=self.tx_display_format_var, value="ASCII", command=self.redisplay_all_logs).pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="HEX", variable=self.tx_display_format_var, value="HEX", command=self.redisplay_all_logs).pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="BIN", variable=self.tx_display_format_var, value="BIN", command=self.redisplay_all_logs).pack(anchor="w", padx=10)

        customtkinter.CTkLabel(self.format_frame, text="TX Encode Format").pack(pady=10)
        customtkinter.CTkRadioButton(self.format_frame, text="ASCII", variable=self.tx_format_var, value="ASCII").pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="HEX", variable=self.tx_format_var, value="HEX").pack(anchor="w", padx=10)
        customtkinter.CTkRadioButton(self.format_frame, text="BIN", variable=self.tx_format_var, value="BIN").pack(anchor="w", padx=10, pady=5)

        # --- Serial Settings ---
        self.serial_settings_frame = customtkinter.CTkFrame(self.control_frame)
        self.serial_settings_frame.pack(pady=10, padx=10, fill="x")

        customtkinter.CTkLabel(self.serial_settings_frame, text="Serial Parameters").pack(pady=5)

        # Byte Size
        customtkinter.CTkLabel(self.serial_settings_frame, text="Byte Size").pack(anchor="w", padx=10)
        self.bytesize_var = customtkinter.StringVar(value="8")
        self.bytesize_menu = customtkinter.CTkOptionMenu(self.serial_settings_frame, variable=self.bytesize_var, values=["8", "7", "6", "5"])
        self.bytesize_menu.pack(fill="x", padx=10, pady=(0, 5))

        # Parity
        customtkinter.CTkLabel(self.serial_settings_frame, text="Parity").pack(anchor="w", padx=10)
        self.parity_var = customtkinter.StringVar(value="None")
        self.parity_menu = customtkinter.CTkOptionMenu(self.serial_settings_frame, variable=self.parity_var, values=["None", "Even", "Odd", "Mark", "Space"])
        self.parity_menu.pack(fill="x", padx=10, pady=(0, 5))

        # Stop Bits
        customtkinter.CTkLabel(self.serial_settings_frame, text="Stop Bits").pack(anchor="w", padx=10)
        self.stopbits_var = customtkinter.StringVar(value="1")
        self.stopbits_menu = customtkinter.CTkOptionMenu(self.serial_settings_frame, variable=self.stopbits_var, values=["1", "1.5", "2"])
        self.stopbits_menu.pack(fill="x", padx=10, pady=(0, 5))


        # --- Time Filter ---
        self.filter_frame = customtkinter.CTkFrame(self.control_frame)
        self.filter_frame.pack(pady=10, padx=10, fill="x")
        customtkinter.CTkLabel(self.filter_frame, text="Filter by Time").pack(pady=5)
        customtkinter.CTkLabel(self.filter_frame, text="Start (HH:MM:SS.ms)").pack(anchor="w", padx=10)
        self.start_time_entry = customtkinter.CTkEntry(self.filter_frame, placeholder_text="HH:MM:SS.ms")
        self.start_time_entry.pack(fill="x", padx=10)
        customtkinter.CTkLabel(self.filter_frame, text="End (HH:MM:SS.ms)").pack(anchor="w", padx=10, pady=(5,0))
        self.end_time_entry = customtkinter.CTkEntry(self.filter_frame, placeholder_text="HH:MM:SS.ms")
        self.end_time_entry.pack(fill="x", padx=10)
        self.filter_button = customtkinter.CTkButton(self.filter_frame, text="Filter", command=self.filter_logs)
        self.filter_button.pack(pady=10)
        self.clear_button = customtkinter.CTkButton(self.filter_frame, text="Clear", command=self.clear_filter)
        self.clear_button.pack(pady=5)

        # --- Bottom Frame ---
        self.bottom_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.send_entry = customtkinter.CTkEntry(self.bottom_frame, placeholder_text="Enter data to send")
        self.send_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.send_entry.bind("<Return>", self.send_data_event)
        self.send_button = customtkinter.CTkButton(self.bottom_frame, text="Send", command=self.send_data)
        self.send_button.grid(row=0, column=1, padx=10, pady=10)

    def get_available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No ports found"]

    def refresh_ports(self):
        self.port_menu.configure(values=self.get_available_ports())

    def toggle_connection(self):
        if self.is_connected:
            self.is_connected = False
            if self.read_thread:
                self.read_thread.join()
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.connect_button.configure(text="Connect")
            self.port_menu.configure(state="normal")
            self.baud_entry.configure(state="normal")
            self.refresh_button.configure(state="normal")
            self.bytesize_menu.configure(state="normal")
            self.parity_menu.configure(state="normal")
            self.stopbits_menu.configure(state="normal")
        else:
            try:
                port = self.port_menu.get()
                baud_rate_str = self.baud_entry.get()
                if not baud_rate_str.isdigit():
                    self.add_log_entry("Error: Baud rate must be an integer.", "error")
                    return
                baud_rate = int(baud_rate_str)

                bytesize = int(self.bytesize_var.get())
                parity_map = {"None": serial.PARITY_NONE, "Even": serial.PARITY_EVEN, "Odd": serial.PARITY_ODD, "Mark": serial.PARITY_MARK, "Space": serial.PARITY_SPACE}
                parity = parity_map[self.parity_var.get()]
                stopbits_map = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}
                stopbits = stopbits_map[self.stopbits_var.get()]

                self.serial_port = serial.Serial(port=port, 
                                                 baudrate=baud_rate, 
                                                 bytesize=bytesize, 
                                                 parity=parity, 
                                                 stopbits=stopbits, 
                                                 timeout=0.1)
                
                self.is_connected = True
                self.connect_button.configure(text="Disconnect")
                self.port_menu.configure(state="disabled")
                self.baud_entry.configure(state="disabled")
                self.refresh_button.configure(state="disabled")
                self.bytesize_menu.configure(state="disabled")
                self.parity_menu.configure(state="disabled")
                self.stopbits_menu.configure(state="disabled")

                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
            except (serial.SerialException, ValueError) as e:
                self.add_log_entry(f"Error: {e}", "error")

    def read_from_port(self):
        while self.is_connected:
            try:
                if self.serial_port and self.serial_port.is_open:
                    data = self.serial_port.readline()
                    if data:
                        self.after(0, self.add_log_entry, data, "rx")
                else:
                    break
            except serial.SerialException:
                break
        self.after(0, self.handle_disconnection)

    def handle_disconnection(self):
        if self.is_connected:
            self.add_log_entry("Serial port disconnected.", "error")
            self.toggle_connection()

    def send_data_event(self, event):
        self.send_data()

    def send_data(self):
        if not self.is_connected:
            self.add_log_entry("Not connected.", "error")
            return
        data_str = self.send_entry.get()
        if data_str:
            try:
                data_bytes = self.format_data_to_send(data_str)
                self.serial_port.write(data_bytes)
                self.add_log_entry(data_bytes, "tx")
                self.send_entry.delete(0, 'end') # Clear the entry box
            except Exception as e:
                self.add_log_entry(f"Error sending data: {e}", "error")

    def format_data_to_send(self, data_str):
        format_type = self.tx_format_var.get()
        if format_type == "ASCII": return data_str.encode('utf-8')
        if format_type == "HEX": return bytes.fromhex(data_str.replace(' ', ''))
        if format_type == "BIN":
            clean_data_str = data_str.replace(' ', '')
            return int(clean_data_str, 2).to_bytes((len(clean_data_str) + 7) // 8, byteorder='big')
        return b''

    def format_display_data(self, data_bytes, format_type):
        if format_type == "ASCII":
            return data_bytes.decode('utf-8', errors='replace').strip()
        if format_type == "HEX":
            return data_bytes.hex(' ').upper()
        if format_type == "BIN":
            return ' '.join(f"{byte:08b}"[i:i+4] for byte in data_bytes for i in (0, 4))
        return ""

    def add_log_entry(self, data, source):
        log_item = {"timestamp": datetime.now(), "data": data, "source": source}
        self.log_data.append(log_item)
        self.display_log_item(log_item, scroll=True)

    def display_log_item(self, log_item, scroll=False):
        timestamp_str = log_item["timestamp"].strftime("%H:%M:%S.%f")[:-3]
        source = log_item["source"]
        data = log_item["data"]

        log_frame = customtkinter.CTkFrame(self.display_frame, fg_color="transparent")

        if source == "error":
            log_label = customtkinter.CTkLabel(log_frame, text=f"[{timestamp_str}] {data}", text_color="red", wraplength=700)
            log_label.pack(padx=10, pady=5, anchor="w")
            log_frame.pack(anchor="w", pady=2, padx=5, fill="x")
        else:
            display_format = self.rx_display_format_var.get() if source == "rx" else self.tx_display_format_var.get()
            
            prefix = ""
            if display_format == "HEX": prefix = "0x"
            if display_format == "BIN": prefix = "0b"

            formatted_data = self.format_display_data(data, display_format)
            anchor = "w" if source == "rx" else "e"
            bg_color = "#343638" if source == "rx" else "#1f6aa5"

            bubble = customtkinter.CTkFrame(log_frame, fg_color=bg_color, corner_radius=10)
            
            # Create a frame inside the bubble to hold prefix and data
            content_frame = customtkinter.CTkFrame(bubble, fg_color="transparent")
            content_frame.pack(padx=10, pady=5)

            if prefix:
                prefix_label = customtkinter.CTkLabel(content_frame, text=prefix, text_color="gray")
                prefix_label.pack(side="left")

            log_label = customtkinter.CTkLabel(content_frame, text=formatted_data, text_color="white", wraplength=480, justify="left")
            log_label.pack(side="left")

            timestamp_label = customtkinter.CTkLabel(log_frame, text=timestamp_str, text_color="gray")

            if anchor == "w":
                bubble.pack(anchor="w")
                timestamp_label.pack(anchor="w", padx=10)
            else:
                bubble.pack(anchor="e")
                timestamp_label.pack(anchor="e", padx=10)
            log_frame.pack(anchor=anchor, pady=2, padx=5, fill="x")

        if self.auto_scroll_var.get() and scroll:
            self.after(10, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.display_frame._parent_canvas.yview_moveto(1.0)

    def redisplay_all_logs(self, filtered_logs=None):
        scroll_pos = self.display_frame._parent_canvas.yview()[0]
        
        for child in self.display_frame.winfo_children():
            child.destroy()
            
        logs_to_show = filtered_logs if filtered_logs is not None else self.log_data
        for item in logs_to_show:
            self.display_log_item(item, scroll=False)

        self.after(10, lambda: self.display_frame._parent_canvas.yview_moveto(scroll_pos))

    def filter_logs(self):
        try:
            start_str = self.start_time_entry.get()
            end_str = self.end_time_entry.get()
            if not start_str or not end_str:
                self.add_log_entry("Error: Start and end times required for filtering.", "error")
                return

            today = datetime.now().date()
            start_dt = datetime.combine(today, datetime.strptime(start_str, "%H:%M:%S.%f").time())
            end_dt = datetime.combine(today, datetime.strptime(end_str, "%H:%M:%S.%f").time())

            filtered = [log for log in self.log_data if start_dt <= log["timestamp"] <= end_dt and log["source"] != "error"]
            self.redisplay_all_logs(filtered)
        except ValueError:
            self.add_log_entry("Error: Invalid time format. Use HH:MM:SS.ms", "error")

    def clear_filter(self):
        self.start_time_entry.delete(0, 'end')
        self.end_time_entry.delete(0, 'end')
        self.redisplay_all_logs()

if __name__ == "__main__":
    app = App()
    app.mainloop()

