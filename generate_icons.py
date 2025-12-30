"""Generate PNG icons from SVG for PWA."""
import os

# Create images directory
os.makedirs('static/images', exist_ok=True)

try:
    from PIL import Image, ImageDraw
    
    def create_icon(size, filename):
        """Create a simple controller icon."""
        img = Image.new('RGBA', (size, size), '#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        # Background circle
        margin = size // 8
        draw.ellipse([margin, margin, size - margin, size - margin], fill='#2a2a2a')
        
        # D-pad (left side)
        center_x = size // 3
        center_y = size // 2
        dpad_size = size // 10
        # Horizontal bar
        draw.rectangle([center_x - dpad_size * 2, center_y - dpad_size // 2,
                       center_x + dpad_size * 2, center_y + dpad_size // 2], fill='#00ff00')
        # Vertical bar
        draw.rectangle([center_x - dpad_size // 2, center_y - dpad_size * 2,
                       center_x + dpad_size // 2, center_y + dpad_size * 2], fill='#00ff00')
        
        # ABXY buttons (right side) - diamonds
        btn_x = size * 2 // 3
        btn_y = size // 2
        btn_r = size // 16
        spacing = size // 8
        
        # A (green, bottom)
        draw.ellipse([btn_x - btn_r, btn_y + spacing - btn_r, 
                     btn_x + btn_r, btn_y + spacing + btn_r], fill='#00ff00')
        # B (red, right)
        draw.ellipse([btn_x + spacing - btn_r, btn_y - btn_r,
                     btn_x + spacing + btn_r, btn_y + btn_r], fill='#ff0055')
        # X (blue, left)
        draw.ellipse([btn_x - spacing - btn_r, btn_y - btn_r,
                     btn_x - spacing + btn_r, btn_y + btn_r], fill='#00ccff')
        # Y (yellow, top)
        draw.ellipse([btn_x - btn_r, btn_y - spacing - btn_r,
                     btn_x + btn_r, btn_y - spacing + btn_r], fill='#ffcc00')
        
        # Convert to RGB (no transparency for iOS)
        rgb_img = Image.new('RGB', (size, size), '#1a1a1a')
        rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
        rgb_img.save(filename, 'PNG')
        print(f'Created {filename}')
    
    # Create all required sizes
    create_icon(192, 'static/images/icon-192.png')
    create_icon(512, 'static/images/icon-512.png')
    create_icon(180, 'static/images/apple-touch-icon.png')
    
    print('\n✓ All icons generated successfully!')
    
except ImportError:
    print("Pillow not installed. Installing...")
    import subprocess
    subprocess.run(['pip', 'install', 'Pillow'])
    print("Please run this script again.")
