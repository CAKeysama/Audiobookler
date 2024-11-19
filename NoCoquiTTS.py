import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Scale
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pyttsx3
import threading
import queue


class PDFToAudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 PDF to Audiobook")
        self.root.geometry("600x800")
        self.root.configure(bg="#f0f2f5")

        # Variáveis
        self.file_path = None
        self.current_page = 0
        self.total_pages = 0
        self.is_playing = False
        self.paused = False
        self.stop_playback_flag = threading.Event()
        self.playback_thread = None
        self.audio_queue = queue.Queue()
        self.current_text = ""
        self.current_position = 0

        # pyttsx3 engine inicializado
        self.engine = pyttsx3.init()
        self.engine_lock = threading.Lock()

        # Interface
        self.create_main_interface()

    def create_main_interface(self):
        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Frame do preview
        preview_frame = tk.Frame(main_container, bg="white", bd=2, relief="solid")
        preview_frame.pack(pady=20)
        self.preview_canvas = tk.Canvas(preview_frame, width=400, height=300, bg="white", bd=0, highlightthickness=0)
        self.preview_canvas.pack(padx=10, pady=10)

        # Navegação
        nav_frame = tk.Frame(main_container, bg="#f0f2f5")
        nav_frame.pack(pady=10)
        self.prev_btn = tk.Button(nav_frame, text="◀", command=self.previous_page, font=("Arial", 14),
                                  bg="#4285F4", fg="white", relief="flat", width=3)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.page_label = tk.Label(nav_frame, text="Page: 0/0", font=("Arial", 12), bg="#f0f2f5", fg="#2c3e50")
        self.page_label.pack(side=tk.LEFT, padx=20)
        self.next_btn = tk.Button(nav_frame, text="▶", command=self.next_page, font=("Arial", 14),
                                  bg="#4285F4", fg="white", relief="flat", width=3)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Controles de reprodução
        controls_frame = tk.Frame(main_container, bg="#f0f2f5")
        controls_frame.pack(pady=20)
        self.play_pause_btn = tk.Button(controls_frame, text="▶", command=self.toggle_playback, font=("Arial", 12),
                                        bg="#4285F4", fg="white", relief="flat", width=10, state=tk.DISABLED)
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)

        # Velocidade de leitura
        speed_frame = tk.Frame(main_container, bg="#f0f2f5")
        speed_frame.pack(pady=10)
        tk.Label(speed_frame, text="Voice Speed:", font=("Arial", 10), bg="#f0f2f5", fg="#2c3e50").pack(side=tk.LEFT)
        self.speed_slider = Scale(speed_frame, from_=0.5, to=2.0, value=1.0, length=200, orient="horizontal")
        self.speed_slider.pack(side=tk.LEFT, padx=10)

        # Status
        self.status_label = tk.Label(main_container, text="Ready", font=("Arial", 9), bg="#f0f2f5", fg="#7f8c8d")
        self.status_label.pack(pady=10)

        # Botão de abrir arquivo
        self.choose_file_btn = tk.Button(main_container, text="📁 Choose PDF", command=self.choose_file,
                                         font=("Arial", 12), bg="#4285F4", fg="white", relief="flat")
        self.choose_file_btn.pack(pady=10)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")], title="Select a PDF file")
        if file_path:
            self.file_path = file_path
            self.render_pdf_preview(file_path)
            self.play_pause_btn.config(state=tk.NORMAL)
            self.update_status(f"Loaded: {file_path.split('/')[-1]}")

    def render_pdf_preview(self, file_path, page_number=0):
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)

            if page_number >= total_pages:
                page_number = total_pages - 1
            elif page_number < 0:
                page_number = 0

            page = doc[page_number]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            image.thumbnail((400, 300))
            self.pdf_preview_image = ImageTk.PhotoImage(image)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(200, 150, image=self.pdf_preview_image)

            self.current_page = page_number
            self.total_pages = total_pages
            self.page_label.config(text=f"Page: {page_number + 1}/{total_pages}")
            doc.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading preview: {e}")

    def toggle_playback(self):
        if self.paused:
            self.paused = False
            self.play_pause_btn.config(text="⏸")
            self.start_playback(self.current_text, resume=True)
        elif not self.is_playing:
            self.current_position = 0  # Reseta para o início
            self.start_playback()
        else:
            self.paused = True
            self.is_playing = False
            self.stop_playback_flag.set()
            self.play_pause_btn.config(text="▶")

    def start_playback(self, text=None, resume=False):
        if text is None:
            self.current_text = self.extract_text_from_pdf(self.file_path, self.current_page)
        self.is_playing = True
        self.stop_playback_flag.clear()

        def playback_task():
            with self.engine_lock:
                if resume:
                    text_to_speak = self.current_text[self.current_position:]
                else:
                    text_to_speak = self.current_text

                self.engine.setProperty("rate", int(self.speed_slider.get() * 150))
                self.engine.say(text_to_speak)
                self.engine.runAndWait()

            self.is_playing = False
            self.play_pause_btn.config(text="▶")

        self.playback_thread = threading.Thread(target=playback_task)
        self.playback_thread.start()

    def extract_text_from_pdf(self, file_path, page_number):
        try:
            doc = fitz.open(file_path)
            page = doc[page_number]
            text = page.get_text()
            doc.close()
            return text
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting text: {e}")
            return ""

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_pdf_preview(self.file_path, self.current_page)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_pdf_preview(self.file_path, self.current_page)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToAudioApp(root)
    root.mainloop()
