import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import fitz  # PyMuPDF
import os
import random

class PolygonSelector:
    """
    A GUI application to select a polygonal area on a potentially resized image.
    It stores the coordinates scaled back to their original dimensions.
    """
    def __init__(self, master, image_path, scale_factor):
        self.master = master
        self.master.title("Select Polygon Area - Click points, then close this window.")
        
        # This scale factor is used to convert screen coordinates back to original image coordinates
        self.scale_factor = scale_factor
        self.polygon_points_original_coords = []
        
        # Load the (potentially resized) image for display
        self.pil_image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        
        # Create a Canvas widget sized to the display image
        self.canvas = tk.Canvas(master, width=self.pil_image.width, height=self.pil_image.height)
        self.canvas.pack()
        
        # Add the image to the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.image = self.tk_image  # Keep a persistent reference
        
        # Bind the mouse click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        print("Click on the image to define the vertices of your polygon.")
        print("When you are finished selecting points, simply close the image window.")

    def on_canvas_click(self, event):
        """
        Called on mouse click. Records the click coordinates on the display image,
        converts them to original image coordinates, and provides visual feedback.
        """
        # Get coordinates from the click event (on the resized image)
        click_x, click_y = event.x, event.y
        
        # Convert the screen coordinates back to the original image's dimensions
        original_x = click_x / self.scale_factor
        original_y = click_y / self.scale_factor
        self.polygon_points_original_coords.append((original_x, original_y))
        
        # --- Visual Feedback on the Display Image ---
        # Draw a small red circle at the click position
        radius = 3
        self.canvas.create_oval(click_x - radius, click_y - radius, click_x + radius, click_y + radius, fill="red", outline="red")
        
        # If we have more than one point, draw a line to the previous point
        if len(self.polygon_points_original_coords) > 1:
            # Get the previous click's screen coordinates for drawing
            prev_click_x = self.canvas.coords(self.canvas.find_all()[-2])[0] + radius
            prev_click_y = self.canvas.coords(self.canvas.find_all()[-2])[1] + radius
            self.canvas.create_line(prev_click_x, prev_click_y, click_x, click_y, fill="red", width=2)

def select_polygon_from_pdf(pdf_path, dpi=200):
    """
    Renders a random page, resizes it to fit the screen for selection,
    and returns the polygon coordinates scaled to the original image size.
    """
    # Create a temporary root window to get screen dimensions
    root_temp = tk.Tk()
    root_temp.withdraw()
    screen_width = root_temp.winfo_screenwidth() * 0.9  # Use 90% of screen
    screen_height = root_temp.winfo_screenheight() * 0.9
    root_temp.destroy()

    doc = fitz.open(pdf_path)
    if not doc.page_count:
        print("Error: The PDF has no pages.")
        doc.close()
        return []

    random_page_index = random.randint(0, doc.page_count - 1)
    print(f"\nRendering page {random_page_index + 1} (out of {doc.page_count}) for selection.")
    
    page = doc.load_page(random_page_index)
    pix = page.get_pixmap(dpi=dpi)
    doc.close()
    
    original_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # --- Calculate scale factor and resize if necessary ---
    img_width, img_height = original_img.size
    scale_factor = min(screen_width / img_width, screen_height / img_height)
    
    if scale_factor >= 1.0: # Image is smaller than the screen
        scale_factor = 1.0
        display_img = original_img
        print("Image fits on screen. No resizing needed for selection.")
    else: # Image is larger than the screen
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        display_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Image is too large. Resizing to {new_width}x{new_height} for display.")

    temp_display_image_path = "temp_display_image.png"
    display_img.save(temp_display_image_path)
    
    # --- GUI for Selection ---
    root_selector = tk.Tk()
    app = PolygonSelector(root_selector, temp_display_image_path, scale_factor)
    root_selector.mainloop()
    
    os.remove(temp_display_image_path)
    
    return app.polygon_points_original_coords

def extract_polygon_from_all_pages(pdf_path, polygon_points, dpi=200):
    """
    Extracts the selected polygonal area from every page of the PDF.
    The polygon_points are already scaled for the full-resolution image.
    """
    if not polygon_points or len(polygon_points) < 3:
        print("No valid polygon selected. Exiting.")
        return

    print(f"\nProcessing all pages with {len(polygon_points)}-sided polygon...")
    output_dir = "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Images will be saved in '{output_dir}'.")

    doc = fitz.open(pdf_path)
    
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        mask = Image.new('L', (img.width, img.height), 0)
        ImageDraw.Draw(mask).polygon(polygon_points, outline=255, fill=255)
        
        img.putalpha(mask)
        
        bbox = mask.getbbox()
        if bbox:
            cropped_img = img.crop(bbox)
            output_path = os.path.join(output_dir, f"page_{i+1}_polygon_crop.png")
            cropped_img.save(output_path)
            print(f"Saved: {output_path}")
        else:
            print(f"Warning: Could not define a crop area on page {i+1}.")
            
    doc.close()
    print("\nProcessing complete.")


if __name__ == "__main__":
    root_fd = tk.Tk()
    root_fd.withdraw()
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    root_fd.destroy()

    if pdf_path:
        # Higher DPI gives better quality output, but uses more memory.
        # This value must be consistent between selection and extraction.
        PROCESSING_DPI = 200 
        
        selected_points = select_polygon_from_pdf(pdf_path, dpi=PROCESSING_DPI)
        
        extract_polygon_from_all_pages(pdf_path, selected_points, dpi=PROCESSING_DPI)
    else:
        print("No PDF file selected.")