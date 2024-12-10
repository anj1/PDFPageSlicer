import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import json
from PIL import Image, ImageTk
import os
import copy

class BoundingBoxAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Annotator")
        
        # State variables
        self.pdf_doc = None
        self.current_page = 0
        self.boxes = {}  # {page_num: [boxes]}
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.zoom_level = 2.0  # Initial zoom (same as current)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Controls frame
        controls = tk.Frame(self.root)
        controls.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(controls, text="Open PDF", command=self.load_pdf).pack(side=tk.LEFT)
        tk.Button(controls, text="Save Boxes", command=self.save_boxes).pack(side=tk.LEFT)
        tk.Button(controls, text="Next Page", command=self.next_page).pack(side=tk.LEFT)
        tk.Button(controls, text="Previous Page", command=self.prev_page).pack(side=tk.LEFT)
        tk.Button(controls, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT)
        tk.Button(controls, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT)
        
        # Canvas for PDF display
        self.canvas = tk.Canvas(self.root, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_box)
        self.canvas.bind("<B1-Motion>", self.draw_box)
        self.canvas.bind("<ButtonRelease-1>", self.end_box)
        
    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_doc = fitz.open(file_path)
            self.boxes = {i: [] for i in range(len(self.pdf_doc))}
            self.current_page = 0
            self.display_current_page()
            
    def display_current_page(self):
        if not self.pdf_doc:
            return
            
        page = self.pdf_doc[self.current_page]
        self.page_rect = page.rect
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.config(width=pix.width, height=pix.height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Redraw existing boxes
        for box in self.boxes[self.current_page]:
            self.canvas.create_rectangle(
                box[0]*self.zoom_level,
                box[1]*self.zoom_level,
                box[2]*self.zoom_level,
                box[3]*self.zoom_level,
                outline='red')
            
    def start_box(self, event):
        self.start_x = self.canvas.canvasx(event.x)/self.zoom_level
        self.start_y = self.canvas.canvasy(event.y)/self.zoom_level
        
    def draw_box(self, event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
            
        cur_x = self.canvas.canvasx(event.x)/self.zoom_level
        cur_y = self.canvas.canvasy(event.y)/self.zoom_level
        
        self.current_rect = self.canvas.create_rectangle(
            self.start_x*self.zoom_level,
            self.start_y*self.zoom_level,
            cur_x*self.zoom_level,
            cur_y*self.zoom_level,
            outline='red')
    
    def normalize_coords(self, coords):
        #nrm_coords = [c / self.zoom_level for c in coords]
        nrm_coords = copy.deepcopy(coords)
        nrm_coords[1], nrm_coords[3] = self.page_rect.height - nrm_coords[3], self.page_rect.height - nrm_coords[1]
        return nrm_coords

    def normalize_boxes(self):
        nrm_boxes = {}
        for page_num, boxes in self.boxes.items():
            nrm_boxes[page_num] = []
            #self.boxes[page_num] = [self.normalize_coords(box) for box in boxes]
            for box in boxes:
                nrm_boxes[page_num].append(self.normalize_coords(box))
        return nrm_boxes

    def end_box(self, event):
        if self.current_rect:
            coords = self.canvas.coords(self.current_rect)
            coords = [c / self.zoom_level for c in coords]

            self.boxes[self.current_page].append(coords)
            self.current_rect = None
            
    def next_page(self):
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.display_current_page()
            
    def prev_page(self):
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            
    def save_boxes(self):
        nrm_boxes = self.normalize_boxes()

        if not self.pdf_doc:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(nrm_boxes, f)
            messagebox.showinfo("Success", "Boxes saved successfully")

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.display_current_page()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.display_current_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = BoundingBoxAnnotator(root)
    root.mainloop()