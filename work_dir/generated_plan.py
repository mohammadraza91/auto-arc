import ezdxf

# --- Constants for Plot Dimensions and Wall Thickness ---
PLOT_WIDTH = 30.0  # feet
PLOT_LENGTH = 40.0 # feet
WALL_THICKNESS = 0.5 # feet (6 inches) - Used conceptually for spacing, not drawn explicitly as double lines

# --- Document Setup ---
doc = ezdxf.new("R2010") # DXF R2010 format
msp = doc.modelspace()

# Set drawing units to feet (INSUNITS=13 for feet)
# This primarily informs CAD software how to interpret drawing units.
doc.header["$INSUNUNITS"] = 13 # 13 for feet
doc.header["$MEASUREMENT"] = 0 # 0 for Imperial

# Define Layers
doc.layers.new("PLOT_BOUNDARY", dxfattribs={"color": 1})     # Red
doc.layers.new("WALLS", dxfattribs={"color": 7})             # White/Black
doc.layers.new("ROOM_LABELS", dxfattribs={"color": 4})       # Cyan
doc.layers.new("DOORS_WINDOWS", dxfattribs={"color": 3})     # Green
doc.layers.new("DIMENSIONS", dxfattribs={"color": 2})        # Yellow

# --- Plot Outline ---
# Draw the outer boundary of the plot as a closed LWPOLYLINE from (0,0)
boundary_coords = [
    (0, 0),
    (PLOT_WIDTH, 0),
    (PLOT_WIDTH, PLOT_LENGTH),
    (0, PLOT_LENGTH),
    (0, 0) # Close the loop
]
msp.add_lwpolyline(boundary_coords, dxfattribs={"layer": "PLOT_BOUNDARY", "linewidth": 0.2})

# --- Helper Functions for Drawing Elements ---

def add_wall_segment(p1, p2):
    """Adds a single line segment representing a wall."""
    msp.add_line(p1, p2, dxfattribs={"layer": "WALLS"})

def add_room_label(text, center_x, center_y, height=1.0):
    """Adds a text label for a room at a given center point."""
    msp.add_text(text, dxfattribs={"layer": "ROOM_LABELS", "height": height}).set_placement(
        (center_x, center_y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

def add_door(p1_open, p2_open, swing_direction="in", layer="DOORS_WINDOWS"):
    """
    Adds a simplified door symbol (a line across the opening).
    p1_open, p2_open define the ends of the wall opening.
    """
    mid_x = (p1_open[0] + p2_open[0]) / 2
    mid_y = (p1_open[1] + p2_open[1]) / 2

    # Draw a small line perpendicular to the opening to indicate a door.
    # This is a very basic representation.
    if abs(p1_open[0] - p2_open[0]) > abs(p1_open[1] - p2_open[1]): # Horizontal opening
        msp.add_line((mid_x, mid_y - 0.75), (mid_x, mid_y + 0.75), dxfattribs={"layer": layer})
    else: # Vertical opening
        msp.add_line((mid_x - 0.75, mid_y), (mid_x + 0.75, mid_y), dxfattribs={"layer": layer})

def add_window(p1_open, p2_open, layer="DOORS_WINDOWS"):
    """
    Adds a simplified window symbol (double lines) across an opening.
    p1_open, p2_open define the ends of the wall opening.
    """
    msp.add_line(p1_open, p2_open, dxfattribs={"layer": layer})
    mid_x = (p1_open[0] + p2_open[0]) / 2
    mid_y = (p1_open[1] + p2_open[1]) / 2
    if abs(p1_open[0] - p2_open[0]) > abs(p1_open[1] - p2_open[1]): # Horizontal opening
        msp.add_line((p1_open[0], mid_y), (p2_open[0], mid_y), dxfattribs={"layer": layer})
    else: # Vertical opening
        msp.add_line((mid_x, p1_open[1]), (mid_x, p2_open[1]), dxfattribs={"layer": layer})


# --- Internal Floor Plan Layout (2BHK) ---
# All coordinates are in feet, relative to (0,0) as the bottom-left of the plot.

# Major Partitions
# Vertical wall at X=18.0, from (18,0) to (18,40)
add_wall_segment((18, 0), (18, PLOT_LENGTH))
# Horizontal wall at Y=18.0, from (0,18) to (30,18)
add_wall_segment((0, 18), (PLOT_WIDTH, 18))

# 1. Living / Dining Area (18' x 18')
# Bounding box: (0,0) to (18,18)
add_room_label("LIVING / DINING", 9, 9, height=1.5)
add_door((8,0), (10,0)) # Main Entrance (2ft wide)
add_window((0, 4), (0, 8)) # Window on left wall

# 2. Kitchen (12' x 12')
# Bounding box: (18,0) to (30,12)
add_wall_segment((18, 12), (30, 12)) # Top wall of kitchen
add_room_label("KITCHEN", 24, 6, height=1.0)
add_door((18, 8), (18, 10)) # Door from Living Area
add_window((30, 4), (30, 8)) # Window on right wall

# 3. Common Toilet (6' x 6')
# Bounding box: (18,12) to (24,18)
add_wall_segment((24, 12), (24, 18)) # Right wall of common toilet
add_room_label("C. TOILET", 21, 15, height=0.8)
add_door((24, 14), (24, 16)) # Door from passage/utility area
add_window((21, 18), (23, 18)) # Window on top wall

# 4. Utility Area (6' x 6')
# Bounding box: (24,12) to (30,18)
add_room_label("UTILITY", 27, 15, height=0.8)
add_window((30, 14), (30, 16)) # Window on right wall

# 5. Bedroom 2 (18' x 11')
# Bounding box: (0,18) to (18,29)
add_wall_segment((0, 29), (18, 29)) # Top wall of Bedroom 2
add_room_label("BEDROOM 2", 9, 23.5, height=1.2)
add_door((18, 22), (18, 24)) # Door from central hallway
add_window((0, 22), (0, 26)) # Window on left wall

# 6. Master Bedroom (18' x 11')
# Bounding box: (0,29) to (18,40)
add_room_label("MASTER BEDROOM", 9, 34.5, height=1.2)
add_door((18, 33), (18, 35)) # Door from central hallway
add_window((0, 33), (0, 37)) # Window on left wall

# 7. Central Hallway / Passage (12' x 14')
# Bounding box: (18,18) to (30,32)
add_wall_segment((18, 32), (30, 32)) # Top wall of hallway
add_room_label("HALLWAY / PASSAGE", 24, 25, height=1.0)

# 8. Master Toilet (12' x 8')
# Bounding box: (18,32) to (30,40)
add_room_label("M. TOILET", 24, 36, height=0.8)
add_door((18, 35), (18, 37)) # Door from hallway
add_window((24, 40), (28, 40)) # Window on top wall

# --- Dimensions ---
# Set up dimension style
dim_style = doc.dimstyles.get("Standard")
dim_style.set_dxf_attrib("dimtxt", 1.0)  # Text height for dimensions
dim_style.set_dxf_attrib("dimasz", 1.0)  # Arrow size for dimensions
dim_style.set_dxf_attrib("dimexe", 0.5)  # Extension line extension
dim_style.set_dxf_attrib("dimexo", 0.5)  # Extension line offset

# Overall dimensions for the plot
msp.add_linear_dim(
    base=(PLOT_WIDTH / 2, -3), # Position below the plot
    p1=(0, 0),
    p2=(PLOT_WIDTH, 0),
    dxfattribs={"layer": "DIMENSIONS"}
).render()

msp.add_linear_dim(
    base=(-3, PLOT_LENGTH / 2), # Position to the left of the plot
    p1=(0, 0),
    p2=(0, PLOT_LENGTH),
    dxfattribs={"layer": "DIMENSIONS"}
).render()

# --- Title Block / General Information ---
msp.add_text(f"2BHK FLOOR PLAN - {PLOT_WIDTH}x{PLOT_LENGTH} FEET",
             dxfattribs={"layer": "PLOT_BOUNDARY", "height": 2.0}).set_placement(
    (PLOT_WIDTH / 2, -6), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

# --- Save DXF File ---
try:
    doc.saveas("plan.dxf")
    print("DXF floor plan 'plan.dxf' created successfully.")
except ezdxf.DXFValueError as e:
    print(f"Error saving DXF: {e}")