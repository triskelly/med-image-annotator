import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json

class ImageAnnotatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Image Viewer & Annotator")

        # Data
        self.image_paths = []
        self.current_index = 0
        self.annotations = {}
        self.drawing = False
        self.start_x = None
        self.start_y = None

        # GUI Elements
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill="both", expand=True)

        self.setup_menu()

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.save_draw)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.prev_image)

    def setup_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Save Annotations", command=self.save_annotations)
        file_menu.add_command(label="Load Annotations", command=self.load_annotations)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_paths = sorted(
                [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.png', '.jpg'))]
            )
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if not self.image_paths:
            return

        img_path = self.image_paths[self.current_index]
        img = Image.open(img_path)
        img = img.resize((512, 512))  # Resize for consistency
        self.tk_img = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        # Redraw existing annotations for this image
        filename = os.path.basename(img_path)
        if filename in self.annotations:
            for box in self.annotations[filename]:
                x0, y0, x1, y1 = box
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="red")

    def next_image(self, event=None):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image()

    def prev_image(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def start_draw(self, event):
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

    def draw(self, event):
        if self.drawing:
            self.canvas.delete("temp")  # Delete previous temp rectangle
            self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, outline="blue", tags="temp"
            )

    def save_draw(self, event):
        if not self.drawing:
            return
        self.drawing = False

        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        filename = os.path.basename(self.image_paths[self.current_index])

        if filename not in self.annotations:
            self.annotations[filename] = []

        self.annotations[filename].append((x0, y0, x1, y1))

        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red")

    def save_annotations(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".json")
        if save_path:
            with open(save_path, "w") as f:
                json.dump(self.annotations, f)

    def load_annotations(self):
        load_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if load_path:
            with open(load_path, "r") as f:
                self.annotations = json.load(f)
            self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageAnnotatorApp(root)
    root.mainloop()
