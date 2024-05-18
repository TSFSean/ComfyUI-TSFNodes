from pythonosc import dispatcher, osc_server
import threading

class GyroOSC:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        self.server_thread = None
        self.server = None
        self.dispatcher = None
        self.initialized = False
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ip_address": ("STRING", {
                    "multiline": False, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "127.0.0.1"
                }),
                "port": ("INT", {"default": "8000"}),
                "vertical_in_min": ("STRING", {"default": "-1.57"}),
                "vertical_in_max": ("STRING", {"default": "1.57"}),
                "vertical_out_min": ("STRING", {"default": "-100"}),
                "vertical_out_max": ("STRING", {"default": "100"}),
                "tilt_in_min": ("STRING", {"default": "-3.142"}),
                "tilt_in_max": ("STRING", {"default": "3.142"}),
                "tilt_out_min": ("STRING", {"default": "-100"}),
                "tilt_out_max": ("STRING", {"default": "100"}),
                "horizontal_in_min": ("STRING", {"default": "-3.142"}),
                "horizontal_in_max": ("STRING", {"default": "3.142"}),
                "horizontal_out_min": ("STRING", {"default": "-100"}),
                "horizontal_out_max": ("STRING", {"default": "100"})
            }
        }

    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT")
    RETURN_NAMES = ("horizontal","vertical","tilt")
    FUNCTION = "load_gyro_osc"
    CATEGORY = "TSFNodes"


    def load_gyro_osc(self, ip_address, port,
                        vertical_in_min, vertical_in_max, vertical_out_min, vertical_out_max,
                        tilt_in_min, tilt_in_max, tilt_out_min, tilt_out_max,
                        horizontal_in_min, horizontal_in_max, horizontal_out_min, horizontal_out_max):
        self.shut_down_existing()
        print("Loading gyro data...")
        if not self.initialized or not self.server_thread.is_alive():
            print("Setting up OSC server with", ip_address, port)
            self.setup_osc_server(ip_address, port)

        # REMAP!
        vertical = self.remap(self.x, float(vertical_in_min), float(vertical_in_max), float(vertical_out_min), float(vertical_out_max))
        tilt = self.remap(self.y, float(tilt_in_min), float(tilt_in_max), float(tilt_out_min), float(tilt_out_max))
        horizontal = self.remap(self.z, float(horizontal_in_min), float(horizontal_in_max), float(horizontal_out_min), float(horizontal_out_max))

        print("Current gyro data:", "H",self.z, "V",self.x, "T",self.y)
        print("Remapped gyro data", "H", round(horizontal), "V",round(vertical),"T", round(tilt))

        return (horizontal, vertical, tilt)
    
    def handle_osc_message(self, unused_addr, args, x, y, z):
        self.x, self.y, self.z = x, y, z

    def setup_osc_server(self, ip, port):
        if self.server_thread and self.server_thread.is_alive():
            self.server.shutdown()  # Properly shut down the existing server
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/gyrosc/gyro", self.handle_osc_message, "Gyro Data")
        self.server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.initialized = True

    def remap(self, value, in_min, in_max, out_min, out_max):
        if (in_max - in_min) == 0:
            return out_min
        return out_min + ((value - in_min) / (in_max - in_min)) * (out_max - out_min)

    #@classmethod
    def IS_CHANGED(s):
        return 

    def shut_down_existing(self):
        print("Shutting down OSC server")
        if self.server:
            self.server.shutdown()  # Properly shut down the server
            self.server.server_close()  # Close the server socket
        if self.server_thread:
            self.server_thread.join()  # Ensure the server thread is closed
            self.server_thread = None
        self.server = None
        self.initialized = False



NODE_CLASS_MAPPINGS = {
    "GyroOSC": GyroOSC
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "GyroOSC": "Gyro OSC"
}

