"""
Generate Architecture Diagram for Automated Attendance System
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.patches as mpatches

# Set up the figure with high DPI for quality
fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

# Color scheme - Professional blue/white
primary_color = '#0d6efd'
secondary_color = '#0a58ca'
text_color = '#212529'
bg_color = '#ffffff'
box_color = '#e7f1ff'
border_color = '#0d6efd'

# Define box style
def create_box(x, y, width, height, label, color=box_color, border_color=border_color):
    """Create a styled box with label"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        edgecolor=border_color,
        facecolor=color,
        linewidth=2
    )
    ax.add_patch(box)
    
    # Add label
    ax.text(x + width/2, y + height/2, label,
            ha='center', va='center',
            fontsize=11, fontweight='bold',
            color=text_color, wrap=True)

# Define arrow style
def create_arrow(x1, y1, x2, y2, color=primary_color, style='->', linewidth=2):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        color=color,
        linewidth=linewidth,
        zorder=1
    )
    ax.add_patch(arrow)

# Title
ax.text(8, 9.5, 'Automated Attendance System Using Computer Vision',
        ha='center', va='center',
        fontsize=18, fontweight='bold',
        color=text_color)

# Section 1: Input Layer (Left)
# Camera Module
create_box(0.5, 7, 2, 1.2, 'Camera Module\n\nCaptures live\nvideo frames', 
           color=box_color, border_color=border_color)

# Section 2: Processing Layer (Center-Left)
# Face Detection Module
create_box(3.5, 7.5, 2, 1.2, 'Face Detection\nModule\n(OpenCV)',
           color=box_color, border_color=border_color)

# Face Encoding Module
create_box(3.5, 5.5, 2, 1.2, 'Face Encoding\nModule\n(face_recognition)\n\n128-dim encodings',
           color=box_color, border_color=border_color)

# Section 3: Database Layer (Center)
# Database
create_box(7, 5, 2.5, 3, 'SQLite Database\n\n• Student Details\n• Face Encodings\n• Attendance Logs\n  (student_id, timestamp,\n   confidence_score)',
           color='#d4edda', border_color='#28a745')

# Section 4: Recognition Layer (Center-Right)
# Face Recognition Module
create_box(10.5, 7.5, 2, 1.2, 'Face Recognition\nModule\n\nCompares encodings\nDistance threshold',
           color=box_color, border_color=border_color)

# Attendance Manager
create_box(10.5, 5.5, 2, 1.2, 'Attendance Manager\n\n• Mark attendance\n• Prevent duplicates\n• Store to database',
           color=box_color, border_color=border_color)

# Section 5: Web Application Layer (Right)
# Flask Web App
create_box(13.5, 4, 2, 4.5, 'Flask Web Application\n\n• Student Registration\n• Take Attendance Page\n• Attendance Records\n• Admin Dashboard',
           color='#fff3cd', border_color='#ffc107')

# Section 6: Output Layer (Bottom)
# Output Section
create_box(5, 1.5, 6, 1.5, 'Output Section\n\n• Attendance Table\n• Visual Dashboard\n• Analytics Reports',
           color='#f8d7da', border_color='#dc3545')

# Arrows - Data Flow
# Camera → Face Detection
create_arrow(2.5, 7.6, 3.5, 8.1, color=primary_color, linewidth=2.5)

# Face Detection → Face Encoding
create_arrow(5.5, 7.6, 5.5, 6.7, color=primary_color, linewidth=2.5)

# Face Encoding → Face Recognition
create_arrow(5.5, 6.1, 10.5, 8.1, color=primary_color, linewidth=2.5)

# Database → Face Recognition (bi-directional)
create_arrow(9.5, 6.5, 10.5, 7.8, color='#28a745', linewidth=2)
create_arrow(10.5, 7.5, 9.5, 6.8, color='#28a745', linewidth=2)

# Face Recognition → Attendance Manager
create_arrow(12.5, 7.5, 12.5, 6.7, color=primary_color, linewidth=2.5)

# Attendance Manager → Database
create_arrow(11.5, 5.5, 9.5, 6.2, color='#28a745', linewidth=2.5)

# Attendance Manager → Web Application
create_arrow(12.5, 5.5, 13.5, 6.2, color=primary_color, linewidth=2.5)

# Web Application → Output
create_arrow(14.5, 4, 11, 2.25, color='#dc3545', linewidth=2.5)

# Database → Output
create_arrow(8.5, 5, 8, 3, color='#28a745', linewidth=2.5)

# Add labels for arrows
ax.text(3, 8.3, 'Video\nFrames', ha='center', fontsize=9, color=primary_color, fontweight='bold')
ax.text(5.8, 7.1, 'Detected\nFaces', ha='center', fontsize=9, color=primary_color, fontweight='bold')
ax.text(8, 7.5, 'Face\nEncodings', ha='center', fontsize=9, color=primary_color, fontweight='bold')
ax.text(10, 7.2, 'Compare', ha='center', fontsize=9, color='#28a745', fontweight='bold')
ax.text(12.5, 7.1, 'Match\nResult', ha='center', fontsize=9, color=primary_color, fontweight='bold')
ax.text(11, 6, 'Store', ha='center', fontsize=9, color='#28a745', fontweight='bold')
ax.text(13, 5.8, 'Update', ha='center', fontsize=9, color=primary_color, fontweight='bold')
ax.text(12.5, 3.2, 'Display', ha='center', fontsize=9, color='#dc3545', fontweight='bold')
ax.text(8.2, 4, 'Query', ha='center', fontsize=9, color='#28a745', fontweight='bold')

# Add section labels
ax.text(1.5, 8.8, 'INPUT', ha='center', fontsize=10, fontweight='bold', 
        color=primary_color, style='italic')
ax.text(4.5, 8.8, 'PROCESSING', ha='center', fontsize=10, fontweight='bold',
        color=primary_color, style='italic')
ax.text(8.25, 8.8, 'STORAGE', ha='center', fontsize=10, fontweight='bold',
        color='#28a745', style='italic')
ax.text(11.5, 8.8, 'RECOGNITION', ha='center', fontsize=10, fontweight='bold',
        color=primary_color, style='italic')
ax.text(14.5, 8.8, 'INTERFACE', ha='center', fontsize=10, fontweight='bold',
        color='#ffc107', style='italic')
ax.text(8, 1, 'OUTPUT', ha='center', fontsize=10, fontweight='bold',
        color='#dc3545', style='italic')

# Add legend
legend_elements = [
    mpatches.Patch(color=box_color, label='Processing Module'),
    mpatches.Patch(color='#d4edda', label='Database'),
    mpatches.Patch(color='#fff3cd', label='Web Application'),
    mpatches.Patch(color='#f8d7da', label='Output'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)

# Save as high-quality PNG
plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("Architecture diagram saved as 'architecture_diagram.png'")

# Also save as SVG for vector format
plt.savefig('architecture_diagram.svg', format='svg', bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Architecture diagram saved as 'architecture_diagram.svg'")

plt.close()
