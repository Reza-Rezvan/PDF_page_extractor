# PDF Polygon Image Extractor

## Description

This Python script provides a graphical user interface (GUI) to extract a custom polygonal area from every page of a PDF document. It is designed to be user-friendly, allowing you to visually select the region you want to crop.

The tool first displays a random page from the selected PDF. If the page is too large for your screen, it automatically resizes it to fit. You can then click to define the vertices of a polygon. The script intelligently translates these clicks back to the original, full-resolution coordinates.

After you close the selection window, the script processes every page of the PDF, cropping the exact polygonal area you defined and saving each one as a high-quality PNG image.

## Features

-   **Interactive Polygon Selection**: Draw any custom shape (not just a rectangle) to define the area you want to extract.
-   **GUI for Ease of Use**: A simple point-and-click interface for selecting the PDF and the crop area.
-   **Handles Large PDFs**: Automatically resizes the selection image to fit your screen, making it easy to work with high-resolution documents.
-   **Accurate Coordinate Scaling**: Intelligently converts coordinates from the resized preview image to the full-resolution original, ensuring precision.
-   **Batch Processing**: Applies the same polygonal crop to every single page of the PDF automatically.
-   **High-Quality Output**: Extractions are performed on high-DPI renderings of the PDF pages to maintain quality. The output images are saved as PNGs with transparency.

## Requirements

Before running the script, you need to have Python installed. The following Python libraries are also required:

-   `PyMuPDF`: For reading and rendering PDF files.
-   `Pillow`: For image manipulation (cropping, resizing).
-   `Tkinter`: For the GUI. (This is usually included with standard Python installations on Windows and macOS).

You can install the necessary libraries using pip:

```bash
pip install PyMuPDF Pillow
```

## How to Use

1.  **Save the Code**: Save the script as a Python file (e.g., `pdf_extractor.py`).

2.  **Run the Script**: Open a terminal or command prompt, navigate to the directory where you saved the file, and execute it:
    ```bash
    python pdf_extractor.py
    ```

3.  **Select a PDF**: A file dialog will pop up. Choose the PDF file you wish to process.

4.  **Define the Polygon**:
    -   A new window will appear, showing a random page from your PDF.
    -   Click on the image to place the corners (vertices) of the polygon you want to extract.
    -   Red dots and lines will appear to give you visual feedback on your selection.
    -   You need to select at least 3 points to form a valid polygon.

5.  **Confirm Selection**: Once you are satisfied with your selection, simply **close the image window**.

6.  **Processing**: The script will begin processing in the background. You will see progress updates in the terminal.

## Output

The script will create a new folder named `extracted_images` in the same directory where the script is located.

Inside this folder, you will find the cropped images, named sequentially:
-   `page_1_polygon_crop.png`
-   `page_2_polygon_crop.png`
-   ...and so on for every page in the PDF.

The output images are PNG files with a transparent background, containing only the polygonal area you selected.

## Configuration

You can adjust the quality of the output images by changing the `PROCESSING_DPI` variable at the bottom of the script:

```python
if __name__ == "__main__":
    # ...
    # Higher DPI gives better quality output, but uses more memory.
    # This value must be consistent between selection and extraction.
    PROCESSING_DPI = 200 # <-- Change this value if needed
    # ...
```

-   A higher DPI (e.g., `300`) will result in larger, higher-quality images but will use more memory and take longer to process.
-   A lower DPI (e.g., `150`) will be faster but produce smaller, lower-quality images.

The default value of `200` provides a good balance between quality and performance.