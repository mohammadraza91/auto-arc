import ezdxf

# --- Constants for Drawing Units and Layers ---
# All dimensions are in feet.
WALL_THICKNESS = 0.5  # 6 inches
TEXT_HEIGHT = 1.0     # Height of room labels

LAYER_PLOT_OUTLINE = "PLOT_OUTLINE"
LAYER_WALLS = "WALLS"
LAYER_ROOM_LABELS = "ROOM_LABELS"

COLOR_PLOT_OUTLINE = 7  # White/Black
COLOR_WALLS = 1         # Red
COLOR_ROOM_LABELS = 4   # Cyan

# --- House and Plot Dimensions (in feet) ---
# Plot Dimensions: A reasonable size for a 3BHK house.
PLOT_WIDTH = 70.0
PLOT_DEPTH = 50.0

# House Dimensions (overall footprint, including outer walls)
HOUSE_WIDTH = 50.0
HOUSE_DEPTH = 30.0

# Setbacks (space from plot boundary to house boundary)
# Defines where the house is placed within the plot.
SETBACK_FRONT = 15.0  # From Plot bottom (Y=0) to House bottom
SETBACK_REAR = 5.0    # From House top to Plot top
SETBACK_LEFT = 10.0   # From Plot left (X=0) to House left
SETBACK_RIGHT = 10.0  # From House right to Plot right

# Calculate house origin relative to plot (0,0)
HOUSE_ORIGIN_X = SETBACK_LEFT
HOUSE_ORIGIN_Y = SETBACK_FRONT

# Derived inner house boundaries (clear space inside outer walls)
INNER_HOUSE_X_START = HOUSE_ORIGIN_X + WALL_THICKNESS
INNER_HOUSE_Y_START = HOUSE_ORIGIN_Y + WALL_THICKNESS
INNER_HOUSE_X_END = HOUSE_ORIGIN_X + HOUSE_WIDTH - WALL_THICKNESS
INNER_HOUSE_Y_END = HOUSE_ORIGIN_Y + HOUSE_DEPTH - WALL_THICKNESS

# --- Room Layout Definition ---
# Layout strategy: Front section for a large living room,
# rear section for 3 bedrooms and 1 common washroom.

# 1. Living Room (front section)
LIVING_ROOM_CLEAR_DEPTH = 15.0 # Internal clear depth for the living room
LIVING_ROOM_CLEAR_WIDTH = INNER_HOUSE_X_END - INNER_HOUSE_X_START # Spans full inner house width

# Top Y coordinate for the living room (excluding the wall above it)
LR_TOP_Y = INNER_HOUSE_Y_START + LIVING_ROOM_CLEAR_DEPTH

# 2. Rear Section (3 Bedrooms + 1 Common Washroom)
# This section starts after the living room and its separating wall.
REAR_SECTION_START_Y = LR_TOP_Y + WALL_THICKNESS

# Calculate available depth for rear rooms:
# Total inner depth - Living room depth - Wall separating LR
REAR_SECTION_CLEAR_DEPTH = INNER_HOUSE_Y_END - REAR_SECTION_START_Y

# Calculate available width for rear rooms:
# Spans full inner house width, same as living room.
REAR_SECTION_CLEAR_WIDTH = INNER_HOUSE_X_END - INNER_HOUSE_X_START # 49 ft

# Distribute REAR_SECTION_CLEAR_WIDTH (49 ft) among 3 bedrooms (12.5 ft each)
# and 1 washroom (10 ft), plus 3 internal walls (0.5 ft each).
# Total clear width for rooms = 3 * 12.5 + 10 = 37.5 + 10 = 47.5 ft
# Total wall thickness = 3 * 0.5 = 1.5 ft
# Total required width = 47.5 + 1.5 = 49 ft. This fits perfectly.

ROOM_BED1_CLEAR_WIDTH = 12.5
ROOM_BED2_CLEAR_WIDTH = 12.5
ROOM_BED3_CLEAR_WIDTH = 12.5
ROOM_WASHROOM_CLEAR_WIDTH = 10.0
ROOM_COMMON_CLEAR_DEPTH = REAR_SECTION_CLEAR_DEPTH # All rear rooms have this depth

# --- Create DXF document ---
doc = ezdxf.new("R2010")  # Using DXF 2010 format for broad compatibility
msp = doc.modelspace()    # Get the modelspace

# --- Setup Layers ---
doc.layers.new(LAYER_PLOT_OUTLINE, dxfattribs={"color": COLOR_PLOT_OUTLINE})
doc.layers.new(LAYER_WALLS, dxfattribs={"color": COLOR_WALLS})
doc.layers.new(LAYER_ROOM_LABELS, dxfattribs={"color": COLOR_ROOM_LABELS})

# --- 1. Draw Plot Outline ---
# The plot starts at (0,0) for simplicity.
plot_points = [
    (0, 0),
    (PLOT_WIDTH, 0),
    (PLOT_WIDTH, PLOT_DEPTH),
    (0, PLOT_DEPTH),
    (0, 0) # Close the polyline
]
msp.add_lwpolyline(plot_points, dxfattribs={"layer": LAYER_PLOT_OUTLINE})

# --- 2. Draw House Outer Walls ---
house_outer_points = [
    (HOUSE_ORIGIN_X, HOUSE_ORIGIN_Y),
    (HOUSE_ORIGIN_X + HOUSE_WIDTH, HOUSE_ORIGIN_Y),
    (HOUSE_ORIGIN_X + HOUSE_WIDTH, HOUSE_ORIGIN_Y + HOUSE_DEPTH),
    (HOUSE_ORIGIN_X, HOUSE_ORIGIN_Y + HOUSE_DEPTH),
    (HOUSE_ORIGIN_X, HOUSE_ORIGIN_Y) # Close the polyline
]
msp.add_lwpolyline(house_outer_points, dxfattribs={"layer": LAYER_WALLS})

# --- 3. Draw Internal Walls and Labels ---

# --- Living Room ---
# Define the bounding box for the clear internal space of the living room
lr_bl = (INNER_HOUSE_X_START, INNER_HOUSE_Y_START)
lr_tr = (INNER_HOUSE_X_END, LR_TOP_Y)

# Add label for Living Room
lr_center_x = (lr_bl[0] + lr_tr[0]) / 2
lr_center_y = (lr_bl[1] + lr_tr[1]) / 2
msp.add_mtext(
    "LIVING ROOM\n{:.1f}' x {:.1f}'".format(
        LIVING_ROOM_CLEAR_WIDTH, LIVING_ROOM_CLEAR_DEPTH
    ),
    dxfattribs={
        "layer": LAYER_ROOM_LABELS,
        "char_height": TEXT_HEIGHT,
        "insert": (lr_center_x, lr_center_y),
        "attachment_point": 5 # Middle-center alignment
    }
)

# Draw wall separating Living Room from the rear section
# This wall is placed at LR_TOP_Y, and extends across the internal house width.
# Its center line is at LR_TOP_Y + WALL_THICKNESS / 2.
# So the lines will be drawn at LR_TOP_Y + WALL_THICKNESS
msp.add_line(
    (INNER_HOUSE_X_START, REAR_SECTION_START_Y),
    (INNER_HOUSE_X_END, REAR_SECTION_START_Y),
    dxfattribs={"layer": LAYER_WALLS}
)

# --- Rear Section: Bedrooms and Washroom ---
# Start tracking the current X position for placing rooms
current_x_pos = INNER_HOUSE_X_START
current_y_pos = REAR_SECTION_START_Y

# List of rooms in the rear section to iterate and draw
room_definitions = [
    ("BEDROOM 1", ROOM_BED1_CLEAR_WIDTH, ROOM_COMMON_CLEAR_DEPTH),
    ("BEDROOM 2", ROOM_BED2_CLEAR_WIDTH, ROOM_COMMON_CLEAR_DEPTH),
    ("BEDROOM 3", ROOM_BED3_CLEAR_WIDTH, ROOM_COMMON_CLEAR_DEPTH),
    ("COMMON WASHROOM", ROOM_WASHROOM_CLEAR_WIDTH, ROOM_COMMON_CLEAR_DEPTH),
]

# Draw vertical internal walls and labels for each room in the rear section
for i, (name, width, depth) in enumerate(room_definitions):
    # Calculate bounding box for the current room's clear space
    room_bl_x = current_x_pos
    room_bl_y = current_y_pos
    room_tr_x = current_x_pos + width
    room_tr_y = current_y_pos + depth

    # Add label for the room
    room_center_x = (room_bl_x + room_tr_x) / 2
    room_center_y = (room_bl_y + room_tr_y) / 2
    msp.add_mtext(
        "{}\n{:.1f}' x {:.1f}'".format(name, width, depth),
        dxfattribs={
            "layer": LAYER_ROOM_LABELS,
            "char_height": TEXT_HEIGHT,
            "insert": (room_center_x, room_center_y),
            "attachment_point": 5 # Middle-center
        }
    )

    # Draw vertical wall to the right of the current room (if not the last room)
    if i < len(room_definitions) - 1:
        # The wall line is placed immediately after the room's clear width.
        # Its center will be at (room_tr_x + WALL_THICKNESS / 2).
        wall_line_x = room_tr_x + WALL_THICKNESS / 2
        msp.add_line(
            (wall_line_x, room_bl_y),
            (wall_line_x, room_tr_y),
            dxfattribs={"layer": LAYER_WALLS}
        )
    
    # Advance current_x_pos for the next room (includes current room's width + wall thickness)
    current_x_pos += width
    if i < len(room_definitions) - 1:
        current_x_pos += WALL_THICKNESS

# --- Save the DXF file ---
filename = "plan.dxf"
doc.saveas(filename)
print(f"DXF floor plan '{filename}' created successfully!")

if __name__ == '__main__':
    # Execute the floor plan generation
    print('Generating DXF floor plan...')
    print('DXF file created successfully!')