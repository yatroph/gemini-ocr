import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import google.generativeai as genai
from pathlib import Path
from PIL import Image
import io
import time
import threading

class Windows97OCR:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini OCR - Windows 97 Style")
        self.root.geometry("800x650")
        
        # Windows 97 color scheme
        self.bg_color = "#c0c0c0"
        self.dark_gray = "#808080"
        self.light_gray = "#dfdfdf"
        self.root.configure(bg=self.bg_color)
        
        self.selected_folders = []
        self.output_file = None
        self.model = None
        self.model_name = None
        
        # Setup UI first
        self.setup_ui()
        
        # Then configure API
        self.configure_gemini_api()
    
    def setup_ui(self):
        # Title bar effect
        title_frame = tk.Frame(self.root, bg="#000080", height=30)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Gemini OCR Tool", 
                              bg="#000080", fg="white", font=("MS Sans Serif", 10, "bold"))
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Main container with sunken border
        main_frame = tk.Frame(self.root, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Folder selection section
        folder_frame = tk.LabelFrame(main_frame, text="Folder Selection", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8))
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_frame = tk.Frame(folder_frame, bg=self.bg_color)
        btn_frame.pack(pady=5)
        
        self.select_btn = tk.Button(btn_frame, text="Select Folders (Any Amount)", 
                                    command=self.select_folders,
                                    relief=tk.RAISED, bd=2, 
                                    font=("MS Sans Serif", 8),
                                    bg=self.bg_color, activebackground=self.light_gray)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_label = tk.Label(folder_frame, text="No folders selected", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8))
        self.folder_label.pack(pady=5)
        
        # Output file section
        output_frame = tk.LabelFrame(main_frame, text="Output File", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8))
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_btn_frame = tk.Frame(output_frame, bg=self.bg_color)
        output_btn_frame.pack(pady=5)
        
        self.output_btn = tk.Button(output_btn_frame, text="Choose Output File", 
                                    command=self.select_output,
                                    relief=tk.RAISED, bd=2,
                                    font=("MS Sans Serif", 8),
                                    bg=self.bg_color, activebackground=self.light_gray)
        self.output_btn.pack(side=tk.LEFT, padx=5)
        
        # Model selector button
        self.model_btn = tk.Button(output_btn_frame, text="List Available Models", 
                                   command=self.list_models,
                                   relief=tk.RAISED, bd=2,
                                   font=("MS Sans Serif", 8),
                                   bg=self.bg_color, activebackground=self.light_gray)
        self.model_btn.pack(side=tk.LEFT, padx=5)
        
        self.output_label = tk.Label(output_frame, text="No output file selected", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8))
        self.output_label.pack(pady=5)
        
        # Progress bar section
        progress_bar_frame = tk.LabelFrame(main_frame, text="Processing Progress", 
                                          bg=self.bg_color, font=("MS Sans Serif", 8))
        progress_bar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_bar_frame, 
                                           mode='determinate',
                                           length=700)
        self.progress_bar.pack(padx=10, pady=10)
        
        self.progress_label = tk.Label(progress_bar_frame, 
                                      text="0 / 0 images processed (0%)",
                                      bg=self.bg_color, 
                                      font=("MS Sans Serif", 8))
        self.progress_label.pack(pady=5)
        
        # Progress section
        progress_frame = tk.LabelFrame(main_frame, text="Progress Log", 
                                       bg=self.bg_color, font=("MS Sans Serif", 8))
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.progress_text = scrolledtext.ScrolledText(progress_frame, 
                                                       height=12, 
                                                       font=("Courier New", 8),
                                                       bg="white", fg="black")
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Process button
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.process_btn = tk.Button(button_frame, text="START OCR PROCESSING", 
                                     command=self.start_processing,
                                     relief=tk.RAISED, bd=3,
                                     font=("MS Sans Serif", 10, "bold"),
                                     bg=self.bg_color, activebackground=self.light_gray,
                                     height=2, width=25)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.dark_gray, relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8),
                                     anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=2, pady=1)
    
    def configure_gemini_api(self):
        """Configure Gemini API after UI is ready"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.log_progress("WARNING: GEMINI_API_KEY not found in environment!\n")
            self.status_label.config(text="API Key Missing!")
            return
        
        genai.configure(api_key=api_key)
        
        # Use the BEST models for OCR in priority order
        model_names = [
            'gemini-2.0-flash-exp',     # Fast experimental
            'gemini-1.5-flash',         # Very reliable
            'gemini-1.5-pro',           # Most accurate
        ]
        
        self.log_progress("Initializing Gemini API...\n")
        
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                self.log_progress(f"✓ Successfully loaded: {model_name}\n")
                self.status_label.config(text=f"Ready - Using {model_name}")
                return
            except Exception as e:
                self.log_progress(f"✗ Could not load {model_name}: {str(e)}\n")
                continue
        
        self.log_progress("\nERROR: Could not load any Gemini model!\n")
        self.status_label.config(text="Model Loading Failed!")
        messagebox.showerror("Error", "Could not load any Gemini model!")
    
    def select_folders(self):
        base_dir = filedialog.askdirectory(title="Select the folder containing subfolders")
        if not base_dir:
            return
        
        # Get all subdirectories
        folders = [f for f in Path(base_dir).iterdir() if f.is_dir()]
        
        self.selected_folders = sorted(folders)
        self.folder_label.config(text=f"Selected {len(self.selected_folders)} folders from:\n{base_dir}")
        self.status_label.config(text=f"Loaded {len(self.selected_folders)} folders")
        self.log_progress(f"Loaded {len(self.selected_folders)} folders from {base_dir}\n")
    
    def select_output(self):
        self.output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if self.output_file:
            self.output_label.config(text=f"Output: {self.output_file}")
            self.status_label.config(text="Output file selected")
    
    def list_models(self):
        """List all available Gemini models"""
        if not os.environ.get("GEMINI_API_KEY"):
            messagebox.showerror("Error", "GEMINI_API_KEY not set!")
            return
        
        try:
            models_info = "Available Gemini Models:\n\n"
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models_info += f"• {m.name}\n"
            
            messagebox.showinfo("Available Models", models_info)
            self.log_progress("\n" + models_info + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Could not list models: {str(e)}")
    
    def log_progress(self, message):
        self.progress_text.insert(tk.END, message)
        self.progress_text.see(tk.END)
        self.root.update()
    
    def update_progress_bar(self, current, total):
        """Update the progress bar and label"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"{current} / {total} images processed ({percentage:.1f}%)")
        else:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0 / 0 images processed (0%)")
        self.root.update()
    
    def ocr_image_single_pass(self, image_path):
        """Perform FAST single-pass OCR with better error handling"""
        try:
            img = Image.open(image_path)
            
            # Convert image if needed (some formats cause issues)
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Single comprehensive prompt
            prompt = """Extract ALL text from this image exactly as shown.

For math notation:
- Superscripts: x^2, y^3
- Subscripts: x_1, a_n  
- Square roots: sqrt(x)
- Fractions: a/b

End each paragraph with semicolon ;
End each equation with semicolon ;

Extract now:"""
            
            response = self.model.generate_content([prompt, img])
            
            # Check if response has text
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                return f"[ERROR: Empty response for {image_path.name}]\n"
            
        except Exception as e:
            error_msg = str(e)
            # Log more specific error info
            return f"[ERROR processing {image_path.name}: {error_msg}]\n"
    
    def start_processing(self):
        if not self.model:
            messagebox.showerror("Error", "GEMINI_API_KEY not found in environment variables!")
            return
        
        if not self.selected_folders:
            messagebox.showwarning("Warning", "Please select folders first!")
            return
        
        if not self.output_file:
            messagebox.showwarning("Warning", "Please select output file first!")
            return
        
        self.log_progress(f"Using model: {self.model_name}\n")
        
        # Run in separate thread to not block GUI
        threading.Thread(target=self.process_all, daemon=True).start()
    
    def process_all(self):
        self.process_btn.config(state=tk.DISABLED)
        
        self.log_progress("\n" + "="*60 + "\n")
        self.log_progress(f"STARTING FAST OCR PROCESSING\n")
        self.log_progress("="*60 + "\n\n")
        
        # Build a set of unique image files to avoid duplicates
        seen_images = set()
        all_images = []
        
        for folder in self.selected_folders:
            image_files = sorted(
                list(folder.glob("*.jpg")) + 
                list(folder.glob("*.jpeg")) + 
                list(folder.glob("*.JPG")) + 
                list(folder.glob("*.JPEG")) +
                list(folder.glob("*.png")) + 
                list(folder.glob("*.PNG"))
            )
            for img_file in image_files:
                # Use absolute path as unique key
                img_key = str(img_file.resolve())
                if img_key not in seen_images:
                    seen_images.add(img_key)
                    all_images.append((folder, img_file))
        
        total_images = len(all_images)
        self.log_progress(f"Total unique images to process: {total_images}\n\n")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                successful = 0
                failed = 0
                current_folder = None
                
                for idx, (folder, img_file) in enumerate(all_images, 1):
                    # Write folder header if this is a new folder
                    if folder != current_folder:
                        current_folder = folder
                        self.log_progress(f"\n{'='*60}\n")
                        self.log_progress(f"FOLDER: {folder.name}\n")
                        self.log_progress(f"{'='*60}\n")
                        outfile.write(f"\n{'='*60}\n")
                        outfile.write(f"FOLDER: {folder.name}\n")
                        outfile.write(f"{'='*60}\n\n")
                    
                    self.update_progress_bar(idx, total_images)
                    self.log_progress(f"  [{idx}/{total_images}] {img_file.name}\n")
                    self.status_label.config(text=f"[{idx}/{total_images}]: {img_file.name}")
                    
                    try:
                        result = self.ocr_image_single_pass(img_file)
                        
                        if "[ERROR" in result:
                            failed += 1
                            self.log_progress(f"      [✗] FAILED - {result.strip()}\n")
                            outfile.write(f"\n--- IMAGE: {img_file.name} [FAILED] ---\n")
                            outfile.write(result)
                            outfile.write("\n\n")
                        else:
                            successful += 1
                            self.log_progress(f"      [✓] SUCCESS\n")
                            outfile.write(f"\n--- IMAGE: {img_file.name} ---\n\n")
                            outfile.write(result)
                            outfile.write("\n\n")
                        
                        outfile.flush()
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.5)
                        
                    except Exception as e:
                        failed += 1
                        error_detail = str(e)
                        self.log_progress(f"      [✗] EXCEPTION: {error_detail}\n")
                        outfile.write(f"\n--- IMAGE: {img_file.name} [ERROR] ---\n")
                        outfile.write(f"[EXCEPTION: {error_detail}]\n\n")
                        outfile.flush()
                
                self.log_progress(f"\n{'='*60}\n")
                self.log_progress(f"PROCESSING COMPLETE!\n")
                self.log_progress(f"Total images: {total_images}\n")
                self.log_progress(f"Successful: {successful}\n")
                self.log_progress(f"Failed: {failed}\n")
                self.log_progress(f"Output: {self.output_file}\n")
                self.log_progress(f"{'='*60}\n")
                
                self.update_progress_bar(total_images, total_images)
                self.status_label.config(text=f"Complete! {successful}/{total_images} successful")
                messagebox.showinfo("Success", 
                                   f"OCR processing complete!\n\n"
                                   f"Total: {total_images}\n"
                                   f"Success: {successful}\n"
                                   f"Failed: {failed}\n\n"
                                   f"Output: {self.output_file}")
        
        except Exception as e:
            self.log_progress(f"\nFATAL ERROR: {str(e)}\n")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        
        finally:
            self.process_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = Windows97OCR(root)
    root.mainloop()