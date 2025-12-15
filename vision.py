import cv2
import numpy as np
import sys
import os
import time

# ASCII characters from dark to light
CHARS = " .:-=+*#%@"
# CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
# Reversed for light-on-dark terminals usually, or depend on logic. 
# Let's map brightness 0-255 to index.
# If terminal is dark, high brightness should be 'dense' char (white) or 'light' char?
# Usually @ is 'dense' (white pixel on black screen). . is 'sparse' (black pixel).
# So 255 (white) -> @. 0 (black) -> ' '.

def map_color(r, g, b):
    # ANSI truecolor: \x1b[38;2;R;G;Bm
    return f"\x1b[38;2;{r};{g};{b}m"

def main():
    # Load face cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Get camera index from args
    camera_idx = 0
    if len(sys.argv) > 1:
        try:
            camera_idx = int(sys.argv[1])
        except ValueError:
            pass
            
    cap = cv2.VideoCapture(camera_idx)
    
    # Capture state
    face_stability_counter = 0
    capture_done = False
    save_ascii = False
    
    # Terminal dimensions (approximate or fixed for now)
    # 80 cols is standard. 
    cols = 100
    rows = 50 
    
    # We want to match output aspect ratio. 
    # Terminal characters are roughly twice as tall as they are wide.
    # So we need to squash the height or stretch the width.
    
    if not cap.isOpened():
        sys.stderr.write("Error: Could not open webcam.\n")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # 1. Resize
        # We want final output to be `cols` wide.
        # Aspect ratio of char is ~0.5 (width/height). 
        # So to keep image aspect ratio, we need to resize carefully.
        # Image w/h = 4/3 usually.
        # We want logical w/h = 4/3.
        # Grid w/h = cols/rows.
        # pixel_aspect = 0.5
        # visual_w = cols * 1
        # visual_h = rows * 2
        # visual_ratio = visual_w / visual_h = cols / (rows * 2) = 0.5 * cols/rows
        # We want 0.5 * cols/rows = image_ratio (1.33)
        # cols/rows = 2.66
        # If cols = 100, rows should be ~37.
        
        height, width, _ = frame.shape
        aspect_ratio = width / height
        
        target_width = cols
        target_height = int(target_width / aspect_ratio / 2) 
        
        small_frame = cv2.resize(frame, (target_width, target_height))
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Detect Face (on the small frame for speed, or large frame and scale?)
        # Let's detect on small frame for simplicity and cool low-res effect artifacts
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Create a mask for the face
        # If "shape of face" means ONLY the face, we mask everything else.
        mask = np.zeros_like(gray)
        
        face_found = False
        if len(faces) > 0:
            # Pick the largest face
            faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            # Draw an ellipse as the mask
            center = (x + w//2, y + h//2)
            axes = (w//2, int(h//2 * 1.2)) # Face is usually an oval
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
            face_found = True
        else:
            # If no face, what to do? Show nothing? Or full video?
            # Reqt: "take a shape of of face... visible on the camera"
            # Let's show full video if no face, or maybe just text "NO FACE".
            # Users prefer seeing themselves. Let's strictly follow "shape of face".
            # We'll just mask everything to 0 if no face.
            pass

        # --- Multi-Capture Logic ---
        current_time = time.time()
        
        # Initialize next capture time if first run
        if 'next_capture_time' not in locals():
            next_capture_time = current_time + 5.0
            capture_count = 0
            
        progress_msg = ""
        
        # Check if we are done
        if capture_count >= 2:
            if 'done_signal_sent' not in locals():
                 print("---DONE---")
                 done_signal_sent = True
                 progress_msg = "All captures done. Waiting for close..."
        else:
            # Check timing
            time_left = next_capture_time - current_time
            
            if time_left > 0:
                progress_msg = f"Capture {capture_count + 1} in {time_left:.1f}s..."
            else:
                # Time to capture!
                # Capture irrespective of face
                filename = f"captured_face_{capture_count + 1}.jpg"
                try:
                    cv2.imwrite(filename, frame)
                    # Save ASCII too
                    with open(f"captured_face_{capture_count + 1}.txt", "w") as f:
                        f.write("\n".join(ascii_text_lines))
                except Exception as e:
                    sys.stderr.write(f"Error saving: {e}\n")
                    
                capture_count += 1
                next_capture_time = time.time() + 5.0 # Schedule next
                print(f"---CAPTURED {capture_count}---")
        # ---------------------------

        # 3. Build ASCII
        # Optimization: Build list of strings then join
        output_lines = []
        ascii_text_lines = [] 
        
        # Iterate pixels
        for r in range(target_height):
            line_parts = []
            text_line_parts = []
            for c in range(target_width):
                if face_found and mask[r, c] == 0:
                     line_parts.append(" ") # Background transparent/space
                     text_line_parts.append(" ")
                else:
                    # Get pixel color
                    pixel_b, pixel_g, pixel_r = small_frame[r, c]
                    # Get luminance for char
                    lum = gray[r, c]
                    # Map lum to char index
                    # 0..255 -> 0..len(CHARS)-1
                    char_idx = int((lum / 255) * (len(CHARS) - 1))
                    
                    color_code = map_color(pixel_r, pixel_g, pixel_b)
                    char = CHARS[char_idx]
                    
                    line_parts.append(f"{color_code}{char}")
                    text_line_parts.append(char)
            
            # Reset color at end of line to avoid artifacts? 
            # Or just let next line handle it? Better to reset.
            line_parts.append("\x1b[0m")
            
            # Embed progress bar/msg
            if r == 0 and progress_msg:
                 # Yellow text for info
                 output_lines.append(f"\x1b[38;2;255;255;0m{progress_msg}\x1b[0m") 
            else:
                 output_lines.append("".join(line_parts))
                 
            ascii_text_lines.append("".join(text_line_parts))
            
        # Join all lines
        ascii_frame = "\n".join(output_lines)
        
        # Save ASCII text if needed
        if save_ascii:
            with open("captured_face.txt", "w") as f:
                f.write("\n".join(ascii_text_lines))
            save_ascii = False
        
        # Output with separator
        # We use a specific delimiter unlikely to appear in the ansi soup.
        print(ascii_frame)
        print("---FRAME---")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
