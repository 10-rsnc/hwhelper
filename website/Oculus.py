import tkinter as tk
import pyautogui
import easyocr
import numpy as np
from google import genai
import time
import ctypes

GOOGLE_API_KEY = "AIzaSyDHOoK5eGFG3Xd1X194HXrM-Bd-Kv7XciE"
client = genai.Client(api_key=GOOGLE_API_KEY)
reader = easyocr.Reader(['en', 'ko'], gpu=False)

class HomeworkHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("Oculus")
        self.root.attributes('-topmost', True)
        self.root.geometry("400x600")
        
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        btn_color = "#2ecc71"
        text_bg = "#2d2d2d"

        try:
            self.root.update()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            get_parent = ctypes.windll.user32.GetParent
            hwnd = get_parent(self.root.winfo_id())
            rendering_policy = ctypes.c_int(1)
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy))
        except:
            pass

        self.root.configure(bg=bg_color)

        self.label = tk.Label(root, text="navigate to your homework and click scan", 
                              font=("Arial", 10), bg=bg_color, fg=fg_color)
        self.label.pack(pady=10)

        self.scan_btn = tk.Button(root, text="Scan & Solve", command=self.process_homework, 
                                  bg=btn_color, fg="white", font=("Arial", 12, "bold"),
                                  activebackground="#27ae60", relief="flat")
        self.scan_btn.pack(pady=10)

        # Switched to standard tk.Text to hide scrollbar
        self.result_area = tk.Text(root, wrap=tk.WORD, width=45, height=25,
                                   bg=text_bg, fg=fg_color, insertbackground="white",
                                   font=("Consolas", 10), relief="flat")
        self.result_area.pack(pady=10, padx=10)

    def process_homework(self):
        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, "solving...\n")
        self.root.update()

        try:
            screenshot = pyautogui.screenshot()
            img_np = np.array(screenshot)
            
            results = reader.readtext(img_np, paragraph=True, x_ths=0.5)
            full_text = "\n\n".join([res[1] for res in results])

            prompt = f"""
            Analyze this text: "{full_text}"

            TASK:
            1. Identify the question and any provided context/passage.
            2. Solve accurately regardless of subject (Math, Language, Science, etc.).
            3. If it's multiple choice, pick the best option. Otherwise, give a direct answer.

            CONSTRAINTS:
            - If it's random UI text or no question exists, respond ONLY with: "no solvable question detected"
            - If a diagram is required that isn't in the text, state: "diagram missing".

            Answer: (direct answer)
            ---
            Explanation: (brief reasoning)
            """
            
            response = None
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=prompt
                    )
                    break 
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        self.result_area.insert(tk.END, f"Quota hit. Retrying in 2s... ({attempt+1}/3)\n")
                        self.root.update()
                        time.sleep(2)
                    else:
                        raise e 

            if response:
                self.result_area.delete(1.0, tk.END)
                self.result_area.insert(tk.END, response.text)
            else:
                self.result_area.insert(tk.END, "Failed after retries.")
            
        except Exception as e:
            self.result_area.insert(tk.END, f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeworkHelper(root)
    root.mainloop()