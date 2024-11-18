import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import threading
from TTS.api import TTS  # Coqui TTS

class PDFToAudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Audiobook")
        self.root.geometry("450x700")
        self.root.configure(bg="#f8f9fa")

        # Variáveis
        self.file_path = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_preview_image = None

        # Header
        self.title_label = tk.Label(self.root, text="PDF to Audiobook", font=("Arial", 20, "bold"), bg="#f8f9fa", fg="#2c2c2c")
        self.title_label.pack(pady=20)

        # Preview Canvas
        self.preview_canvas = tk.Canvas(self.root, width=300, height=200, bg="#e9ecef", bd=0, highlightthickness=0)
        self.preview_canvas.pack(pady=10)

        # Navegação de página
        self.page_nav_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.page_nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(
            self.page_nav_frame, text="◀ Prev", command=lambda: self.render_pdf_preview(self.file_path, self.current_page - 1),
            bg="#f8f9fa", fg="#4285F4", font=("Arial", 10, "bold"), relief="flat"
        )
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.page_label = tk.Label(self.page_nav_frame, text="Page: 0/0", bg="#f8f9fa", font=("Arial", 10), fg="#6c757d")
        self.page_label.grid(row=0, column=1)

        self.next_btn = tk.Button(
            self.page_nav_frame, text="Next ▶", command=lambda: self.render_pdf_preview(self.file_path, self.current_page + 1),
            bg="#f8f9fa", fg="#4285F4", font=("Arial", 10, "bold"), relief="flat"
        )
        self.next_btn.grid(row=0, column=2, padx=10)

        # Escolher arquivo
        self.choose_file_btn = tk.Button(
            self.root, text="Choose PDF File", command=self.choose_file,
            font=("Arial", 12), bg="#4285F4", fg="white", relief="flat", height=2, width=20
        )
        self.choose_file_btn.pack(pady=10)

        # Botão de conversão
        self.convert_btn = tk.Button(
            self.root, text="Convert to Audio", command=self.convert_to_audio,
            font=("Arial", 12), bg="#4285F4", fg="white", relief="flat", height=2, width=20
        )
        self.convert_btn.pack(pady=20)

        # Loading/Progress bar
        self.progress_bar = Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(pady=20)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.file_path = file_path
            self.render_pdf_preview(file_path)

    def render_pdf_preview(self, file_path, page_number=0):
        """Renderiza uma página do PDF."""
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
            image.thumbnail((300, 200))
            self.pdf_preview_image = ImageTk.PhotoImage(image)

            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(150, 100, image=self.pdf_preview_image)

            self.current_page = page_number
            self.total_pages = total_pages
            self.page_label.config(text=f"Page: {page_number + 1}/{total_pages}")

            doc.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading preview: {e}")

    def convert_to_audio(self):
        """Inicia a conversão para áudio."""
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a PDF file!")
            return

        self.progress_bar.start()

        def task():
            try:
                # Ler PDF
                doc = fitz.open(self.file_path)
                text = ""
                for page in doc:
                    text += page.get_text()

                # Gerar áudio com Coqui TTS
                tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                tts.tts_to_file(text=text, file_path="output_audio.wav")

                messagebox.showinfo("Success", "Audio generated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error converting to audio: {e}")
            finally:
                self.progress_bar.stop()

        threading.Thread(target=task).start()

# Inicializar aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToAudioApp(root)
    root.mainloop()
