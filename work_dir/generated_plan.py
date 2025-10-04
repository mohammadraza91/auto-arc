import ezdxf
from ezdxf.enums import TextEntityAlignment, MTextEntityAlignment

# --- DXF Setup ---
# Create a new DXF document (R2010 for broader compatibility)
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# --- Units and Layers ---
# Drawing units are feet
UNIT_NAME = 'ft'
TEXT_HEIGHT = 2.0  # Height of room labels in feet
SMALL_TEXT_HEIGHT = 1.0 # Height for smaller labels/notes

# Define layers with specific colors
doc.layers.new('PLOT', dxfattribs={'color': 1})  # Red
doc.layers.new('SETBACKS', dxfattribs={'color': 4, 'linetype': 'DASHED'})  # Cyan, dashed
doc.layers.new('WALLS', dxfattribs={'color': 7})  # White/Black
doc.layers.new('ROOM_LABELS', dxfattribs={'color': 2})  # Yellow
doc.layers.new('FEATURES', dxfattribs={'color': 3})  # Green

# Add DASHED linetype definition if not present (ezdxf usually has it, but good to be explicit)
if 'DASHED' not in doc.linetypes:
    pass  # sanitized: removed invalid custom linetype definition
def add_labeled_rectangle(msp, p1, p2, layer, label=None, text_height=TEXT_HEIGHT, color=None):
    """
    Draws a rectangle (as LWPOLYLINE) from two corner points and
    adds a centered text label if provided.
    """
    x1, y1 = p1
    x2, y2 = p2

    # Draw the rectangle using LWPOLYLINE for efficiency and flexibility
    msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
                       dxfattribs={'layer': layer, 'closed': True, 'color': color if color else doc.layers.get(layer).dxf.color})

    # Add label if provided, centered within the rectangle
    if label:
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        msp.add_text(label,
                     dxfattribs={
                         'layer': 'ROOM_LABELS',
                         'height': text_height,
                         'insert': (center_x, center_y),
                         'halign': TextEntityAlignment.CENTER,
                         'valign': TextEntityAlignment.MIDDLE,
                         'color': doc.layers.get('ROOM_LABELS').dxf.color
                     })

# --- Plot Dimensions ---
PLOT_WIDTH = 40  # ft
PLOT_LENGTH = 60 # ft

# --- Setbacks ---
FRONT_SETBACK = 8  # ft
SIDE_SETBACK = 4   # ft (applies to left and right)
BACK_SETBACK = 4   # ft

# --- Coordinates (all in feet, relative to (0,0) as plot bottom-left corner) ---

# 1. Plot Outline
plot_p1 = (0, 0)
plot_p2 = (PLOT_WIDTH, PLOT_LENGTH)
add_labeled_rectangle(msp, plot_p1, plot_p2, 'PLOT', f'Plot {PLOT_WIDTH}x{PLOT_LENGTH} {UNIT_NAME}')

# 2. Setback Lines
# Front setback line
msp.add_line((0, FRONT_SETBACK), (PLOT_WIDTH, FRONT_SETBACK), dxfattribs={'layer': 'SETBACKS'})
# Back setback line
msp.add_line((0, PLOT_LENGTH - BACK_SETBACK), (PLOT_WIDTH, PLOT_LENGTH - BACK_SETBACK), dxfattribs={'layer': 'SETBACKS'})
# Left setback line
msp.add_line((SIDE_SETBACK, 0), (SIDE_SETBACK, PLOT_LENGTH), dxfattribs={'layer': 'SETBACKS'})
# Right setback line
msp.add_line((PLOT_WIDTH - SIDE_SETBACK, 0), (PLOT_WIDTH - SIDE_SETBACK, PLOT_LENGTH), dxfattribs={'layer': 'SETBACKS'})

# Define the buildable area boundaries
BUILD_X1 = SIDE_SETBACK  # 4 ft
BUILD_Y1 = FRONT_SETBACK # 8 ft
BUILD_X2 = PLOT_WIDTH - SIDE_SETBACK   # 36 ft
BUILD_Y2 = PLOT_LENGTH - BACK_SETBACK  # 56 ft

# --- Layout Design within the plot and buildable area ---

# External Features (within plot boundaries, covering front setback area)
add_labeled_rectangle(msp, (0, 0), (12, FRONT_SETBACK), 'FEATURES', 'Parking (12x8 ft)', text_height=SMALL_TEXT_HEIGHT)
add_labeled_rectangle(msp, (12, 0), (PLOT_WIDTH, FRONT_SETBACK), 'FEATURES', 'Garden (28x8 ft)', text_height=SMALL_TEXT_HEIGHT)

# Internal Rooms (within the buildable area: (4,8) to (36,56))

# Front section of the building
add_labeled_rectangle(msp, (BUILD_X1, BUILD_Y1), (16, 20), 'WALLS', 'Bedroom 1 (12x12 ft)') # (4,8) to (16,20)
add_labeled_rectangle(msp, (28, BUILD_Y1), (BUILD_X2, 20), 'WALLS', 'Staircase (8x12 ft)')   # (28,8) to (36,20)

# Middle section of the building
add_labeled_rectangle(msp, (BUILD_X1, 20), (10, 28), 'WALLS', 'Common Toilet (6x8 ft)') # (4,20) to (10,28)
add_labeled_rectangle(msp, (BUILD_X1, 28), (14, 40), 'WALLS', 'Kitchen (10x12 ft)')     # (4,28) to (14,40)
add_labeled_rectangle(msp, (14, 20), (28, 40), 'WALLS', 'Dining Space (14x20 ft)')  # (14,20) to (28,40)

# Back section of the building
add_labeled_rectangle(msp, (BUILD_X1, 40), (26, BUILD_Y2), 'WALLS', 'Bedroom 2 (22x16 ft)') # (4,40) to (26,56)
add_labeled_rectangle(msp, (26, 40), (BUILD_X2, 48), 'WALLS', 'Attached Toilet (10x8 ft)') # (26,40) to (36,48)
add_labeled_rectangle(msp, (26, 48), (BUILD_X2, BUILD_Y2), 'WALLS', 'Master Closet (10x8 ft)') # (26,48) to (36,56)

# --- Save DXF ---
file_name = 'plan.dxf'
doc.saveas(file_name)
print(f"DXF floor plan '{file_name}' created successfully in the current working directory.")