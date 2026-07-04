import customtkinter as ctk
import pyautogui
import time
import os
import re
import json
import threading
from google import genai
from google.genai import errors
from PIL import Image, ImageDraw
import pandas as pd

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

pyautogui.FAILSAFE = True
KEY_FILE = "ace_key.txt"

class AceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ace: Autonomous Desktop Pilot")
        self.geometry("600x700")
        self.client = None

        self.key_frame = ctk.CTkFrame(self)
        self.key_frame.pack(pady=15, padx=15, fill="x")

        self.key_label = ctk.CTkLabel(self.key_frame, text="Gemini API Key:", font=("Segoe UI", 12, "bold"))
        self.key_label.pack(side="left", padx=10, pady=10)

        self.key_entry = ctk.CTkEntry(self.key_frame, placeholder_text="Paste your AIzaSy... key here", width=320, show="*")
        self.key_entry.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.save_key_btn = ctk.CTkButton(self.key_frame, text="Save & Load", width=100, font=("Segoe UI", 12, "bold"), command=self.save_and_load_key)
        self.save_key_btn.pack(side="right", padx=10, pady=10)

        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Segoe UI", 13), wrap="word")
        self.chat_display.pack(pady=10, padx=15, fill="both", expand=True)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=15, padx=15, fill="x")

        self.user_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask Ace to automate something... (or write LIVE_EXCEL)", height=45)
        self.user_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        self.user_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Run 🚀", width=100, height=45, font=("Segoe UI", 13, "bold"), command=self.send_message)
        self.send_btn.pack(side="right", padx=10, pady=10)

        self.check_preexisting_key()

    def log_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def check_preexisting_key(self):
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "r") as f:
                    key = f.read().strip()
                    if key:
                        self.key_entry.insert(0, key)
                        self.client = genai.Client(api_key=key)
                        self.log_to_chat("🤖 Ace", "Welcome back! Your saved API Key is loaded.")
                        return
            except Exception:
                pass
        self.log_to_chat("🤖 Ace", "Hello Aniket! Please paste a fresh Gemini API Key or type LIVE_EXCEL below for an offline test run.")

    def save_and_load_key(self):
        key = self.key_entry.get().strip()
        if not key:
            self.log_to_chat("❌ System", "The key field cannot be left blank.")
            return
        try:
            with open(KEY_FILE, "w") as f:
                f.write(key)
            self.client = genai.Client(api_key=key)
            self.log_to_chat("🔑 System", "API Key configuration successfully updated!")
        except Exception as e:
            self.log_to_chat("❌ System", f"Failed to save local key file token: {e}")

    def send_message(self):
        user_text = self.user_entry.get().strip()
        if not user_text:
            return
        
        self.log_to_chat("👤 Aniket", user_text)
        self.user_entry.delete(0, "end")

        if not self.client and user_text != "LIVE_EXCEL":
            self.log_to_chat("🤖 Ace", "Please load an active API Key before running automation objectives.")
            return

        threading.Thread(target=self.execute_agent_routine, args=(user_text,), daemon=True).start()

    def execute_agent_routine(self, objective):
        if objective == "LIVE_EXCEL":
            self.log_to_chat("🤖 Ace", "Executing hardcoded local macro sequence...")
            pyautogui.press('win'); time.sleep(1)
            pyautogui.write('excel', interval=0.1); time.sleep(1); pyautogui.press('enter'); time.sleep(4)
            pyautogui.press('enter'); time.sleep(1)
            pyautogui.write("Item Name\tCategory\tEstimated Cost\nLaptop Cooling Pad\tGaming\t1500\nMechanical Keyboard\tAccessories\t2500", interval=0.02)
            self.log_to_chat("🤖 Ace", "Finished running offline presentation macros successfully!")
            return

        self.log_to_chat("🤖 Ace", "Taking system snapshot & analyzing visual elements...")
        screenshot_path = "agent_grid_view.png"
        pyautogui.screenshot().save(screenshot_path)
        
        img = Image.open(screenshot_path)
        draw = ImageDraw.Draw(img)
        for x in range(0, img.size[0], 100): draw.line([(x, 0), (x, img.size[1])], fill="red", width=1)
        for y in range(0, img.size[1], 100): draw.line([(0, y), (img.size[0], y)], fill="red", width=1)
        img.save(screenshot_path)

        SYSTEM_INSTRUCTIONS = "You are 'Ace', a computer control engine. Return exactly ONE syntax block: CREATE_SHEET 'details', CLICK X, Y, TYPE 'text', PRESS 'key', or FINISHED."
        prompt = f"Objective: {objective}\nDetermine next action layout coordinate sequence."

        try:
            img_input = Image.open(screenshot_path)
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[img_input, prompt],
                config={'system_instruction': SYSTEM_INSTRUCTIONS}
            )
            action = response.text.strip()
            self.log_to_chat("🧠 Ace Decision", action)
            
            if "FINISHED" in action:
                self.log_to_chat("🤖 Ace", "Goal met completely.")
            elif action.startswith("CREATE_SHEET"):
                sheet_req = re.findall(r"['\"](.*?)['\"]", action)
                if sheet_req:
                    self.log_to_chat("⚡ Tool Active", f"Building matrix spreadsheet layout table for: {sheet_req[0]}")
                    data_prompt = f"Generate realistic comprehensive data metrics rows for: '{sheet_req[0]}'. Return strictly formatted as a single raw clean flat JSON list of text dictionary objects. Do not include markdown wrapped backticks code fences."
                    data_resp = self.client.models.generate_content(model='gemini-2.5-flash', contents=data_prompt)
                    
                    clean_json = data_resp.text.strip()
                    if clean_json.startswith("```"): 
                        clean_json = re.sub(r"^```[a-zA-Z]*\n|```$", "", clean_json, flags=re.MULTILINE).strip()
                    
                    data_list = json.loads(clean_json)
                    df = pd.DataFrame(data_list)
                    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "Ace_App_Output.xlsx")
                    df.to_excel(desktop_path, index=False)
                    os.startfile(desktop_path)
                    self.log_to_chat("📊 Success", "File created cleanly and launched right over your screen background layout!")
            elif action.startswith("CLICK"):
                coords = re.findall(r'\d+', action)
                if coords: pyautogui.click(int(coords[0]), int(coords[1]))
            elif action.startswith("TYPE"):
                text = re.findall(r"'(.*?)'", action)
                if text: pyautogui.write(text[0], interval=0.05)
            elif action.startswith("PRESS"):
                key = re.findall(r"'(.*?)'", action)
                if key: pyautogui.press(key[0])
                
        except Exception as e:
            self.log_to_chat("🤖 Ace Status", f"Error occurred: {e}")
        
        if os.path.exists(screenshot_path):
            try: os.remove(screenshot_path)
            except: pass

if __name__ == "__main__":
    app = AceApp()
    app.mainloop()