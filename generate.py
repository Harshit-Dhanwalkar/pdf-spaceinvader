# --- PDF File Templates ---
PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>

%% Annots Page 1 (also used as overall fields list)
21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /Parent 2 0 R
  /Resources <<
  >>
  /Rotate 0
  /Type /Page
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj


42 0 obj
<< >>
stream

// --- Core PDF JavaScript Setup ---
// Hacky wrapper to work with a callback instead of a string
// This allows app.setInterval to call a named function or an anonymous one.
function setInterval(cb, ms) {
    evalStr = "(" + cb.toString() + ")();";
    return app.setInterval(evalStr, ms);
}

// Simple random number generator (not strictly needed for this version, but harmless)
var rand_seed = Date.now() % 2147483647;
function rand() {
    return rand_seed = rand_seed * 16807 % 2147483647;
}

// --- Game Globals ---
var player_x; // X position of the player
var player_y; // Y position of the player

// Arrays to hold references to PDF form fields (pixels) for each color type
// This allows dynamic coloring by hiding/showing specific pre-colored fields.
var pixel_fields = {
    player: [], // For the player's specific color
    bullet: [], // For bullet color
    enemy: [],  // For enemy color
    blast: [],  // For blast effect color
    off: []     // For the default 'off' or hidden state (e.g., black)
};

var bullets = []; // Array to hold active bullet objects
var enemies = []; // Array to hold falling enemy objects

// Define game colors as global variables for easy reference
var PLAYER_COLOR_NAME = "PLAYER";
var ENEMY_COLOR_NAME = "ENEMY";
var BULLET_COLOR_NAME = "BULLET";
var BLAST_COLOR_NAME = "BLAST";
var OFF_COLOR_NAME = "OFF"; // Represents the hidden/off state of a pixel

var ENEMY_SPAWN_RATE = 3; // How often enemies spawn
var spawn_counter = 0;
var TICK_INTERVAL = 70; // Game refresh rate in milliseconds
var interval = 0; // Interval ID for clearing later

// --- Game Functions ---

// Controls visibility of UI elements
function set_controls_visibility(state) {
    this.getField("T_input").hidden = !state;
    this.getField("B_left").hidden = !state;
    this.getField("B_right").hidden = !state;
    this.getField("B_up").hidden = !state;
    this.getField("B_down").hidden = !state;
    this.getField("B_fire").hidden = !state; // Also hide/show fire button
}

// Initializes the game state
function game_init() {
    // Gather references to pixel field objects for all color variants
    for (var x = 0; x < ###GRID_WIDTH###; ++x) {
        pixel_fields.player[x] = [];
        pixel_fields.bullet[x] = [];
        pixel_fields.enemy[x] = [];
        pixel_fields.blast[x] = [];
        pixel_fields.off[x] = [];
        for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
            // PDF Y-coordinates are inverted for grid-based games (0 is bottom)
            // Store references mapping game (x,y) to PDF field names.
            var pdf_y = ###GRID_HEIGHT### - 1 - y;
            pixel_fields.player[x][y] = this.getField(`P_${x}_${pdf_y}_${PLAYER_COLOR_NAME}`);
            pixel_fields.bullet[x][y] = this.getField(`P_${x}_${pdf_y}_${BULLET_COLOR_NAME}`);
            pixel_fields.enemy[x][y] = this.getField(`P_${x}_${pdf_y}_${ENEMY_COLOR_NAME}`);
            pixel_fields.blast[x][y] = this.getField(`P_${x}_${pdf_y}_${BLAST_COLOR_NAME}`);
            pixel_fields.off[x][y] = this.getField(`P_${x}_${pdf_y}_${OFF_COLOR_NAME}`);
        }
    }

    // Set initial position of the player (center of the grid, near bottom)
    player_x = Math.floor(###GRID_WIDTH### / 2);
    player_y = Math.floor(###GRID_HEIGHT### - 4);

    // Start the game loop (calls game_tick repeatedly)
    interval = setInterval(game_tick, TICK_INTERVAL);

    // Hide the start button after game begins
    this.getField("B_start").hidden = true;

    // Show input box and control buttons
    set_controls_visibility(true);

    // Draw the initial state
    draw();
}

// Sets the visibility of a single "pixel" (form field) based on color
function set_pixel(x, y, state, color_name) {
    // Boundary check for safety
    if (x < 0 || y < 0 || x >= ###GRID_WIDTH### || y >= ###GRID_HEIGHT###) {
        return;
    }

    // Hide all color variants at this position first
    pixel_fields.player[x][y].hidden = true;
    pixel_fields.bullet[x][y].hidden = true;
    pixel_fields.enemy[x][y].hidden = true;
    pixel_fields.blast[x][y].hidden = true;
    pixel_fields.off[x][y].hidden = true;

    if (state) {
        // Show the specific color pixel field
        switch(color_name) {
            case PLAYER_COLOR_NAME:
                pixel_fields.player[x][y].hidden = false;
                break;
            case BULLET_COLOR_NAME:
                pixel_fields.bullet[x][y].hidden = false;
                break;
            case ENEMY_COLOR_NAME:
                pixel_fields.enemy[x][y].hidden = false;
                break;
            case BLAST_COLOR_NAME:
                pixel_fields.blast[x][y].hidden = false;
                break;
            default:
                // If an unknown color is requested, show the 'off' pixel
                pixel_fields.off[x][y].hidden = false;
                break;
        }
    } else {
        // If state is false, show the "off" pixel to clear the space
        pixel_fields.off[x][y].hidden = false;
    }
}

// Moves the player square by (dx, dy) and handles boundary checks
function move_player(dx, dy) {
    player_x += dx;
    player_y += dy;

    // Keep player within horizontal bounds
    if (player_x < 0) {
        player_x = 0;
    } else if (player_x >= ###GRID_WIDTH###) {
        player_x = ###GRID_WIDTH### - 1;
    }

    // Keep player within vertical bounds (player should not go above mid-screen approx)
    var player_upper_bound = Math.floor(###GRID_HEIGHT### / 2);
    if (player_y < player_upper_bound) {
        player_y = player_upper_bound;
    } else if (player_y >= ###GRID_HEIGHT###) {
        player_y = ###GRID_HEIGHT### - 1;
    }
    draw(); // Redraw immediately after moving
}

// Handles user input from the text field (for keyboard controls)
function handle_input(event) {
    var input_char = event.change.toLowerCase(); // Get the character typed

    switch (input_char) {
        case 'w': // Up
        case 'arrowup': // Arrow key support
            move_player(0, -1);
            break;
        case 's': // Down
        case 'arrowdown':
            move_player(0, 1);
            break;
        case 'a': // Left
        case 'arrowleft':
            move_player(-1, 0);
            break;
        case 'd': // Right
        case 'arrowright':
            move_player(1, 0);
            break;
        case ' ': // Fire (Spacebar)
        case '/': // Fire (often used as 'fire' in text-based games)
            fire_bullet();
            break;
    }
    // Clear the input field after processing to allow continuous input
    event.target.value = "";
}


// Create and shoot a bullet
function fire_bullet() {
    bullets.push({ x: player_x, y: player_y - 1, color_name: BULLET_COLOR_NAME });
}

// Update bullets and redraw them
function update_bullets() {
    for (var i = 0; i < bullets.length; ++i) {
        bullets[i].y -= 1; // Move bullet up
    }

    // Remove bullets off screen
    bullets = bullets.filter(function (b) {
        return b.y >= 0;
    });
}

// Draw bullets
function draw_bullets() {
    for (var i = 0; i < bullets.length; ++i) {
        set_pixel(bullets[i].x, bullets[i].y, true, bullets[i].color_name);
    }
}

// Triggers a temporary blast animation at (x, y)
function trigger_blast(x, y) {
    // Set pixel to blast color
    set_pixel(x, y, true, BLAST_COLOR_NAME);

    // After a short delay, set the pixel back to the 'off' state to simulate a flash
    app.setInterval(function() {
        set_pixel(x, y, false, OFF_COLOR_NAME); // Use OFF_COLOR_NAME for proper clearing
    }, BLAST_DURATION);
}

// Create and spawn a new enemy object
function spawn_enemy() {
    var random_x = Math.floor(Math.random() * ###GRID_WIDTH###); // Random X position
    enemies.push({ x: random_x, y: 0, color_name: ENEMY_COLOR_NAME }); // Start at the top row
}

// Update enemies and remove them if off-screen
function update_enemies() {
    // Move existing enemies down
    for (var i = 0; i < enemies.length; ++i) {
        enemies[i].y += 1; // Move down by one pixel
    }

    // Remove enemies off screen (if they go beyond the bottom of the grid)
    enemies = enemies.filter(function (e) {
        return e.y < ###GRID_HEIGHT###; // Keep enemies that are on or above the bottom edge
    });

    // Spawn new enemies periodically
    spawn_counter++;
    if (spawn_counter >= ENEMY_SPAWN_RATE) {
        spawn_enemy();
        spawn_counter = 0; // Reset counter
    }
}

// Draw enemies
function draw_enemies() {
    for (var i = 0; i < enemies.length; ++i) {
        set_pixel(enemies[i].x, enemies[i].y, true, enemies[i].color_name);
    }
}

// Check for collisions between bullets and enemies
function check_collisions() {
    // Iterate through all active bullets
    for (var i = bullets.length - 1; i >= 0; i--) {
        var bullet = bullets[i];

        // Iterate through all active enemies
        for (var j = enemies.length - 1; j >= 0; j--) {
            var enemy = enemies[j];

            // Check if bullet and enemy occupy the same grid coordinates
            if (bullet.x === enemy.x && bullet.y === enemy.y) {
                // Trigger blast animation at collision point
                trigger_blast(bullet.x, bullet.y);

                bullets.splice(i, 1); // Remove the bullet
                enemies.splice(j, 1); // Remove the enemy

                break; // A bullet can only hit one enemy at a time
            }
        }
    }
}

// Draws the current state of the game (player, bullets, and enemies)
function draw() {
    // First, clear the entire grid by setting all pixels to their 'off' state
    for (var x = 0; x < ###GRID_WIDTH###; ++x) {
        for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
            set_pixel(x, y, false, OFF_COLOR_NAME); // Hide all pixels
        }
    }

    // Then, draw the player square at its current position with its current color
    set_pixel(player_x, player_y, true, PLAYER_COLOR_NAME);

    // Draw bullets
    draw_bullets();

    // Draw enemies
    draw_enemies();
}

// The main game loop function, called repeatedly by setInterval
function game_tick() {
    update_bullets();
    update_enemies();
    check_collisions();
    draw();
}

// --- Initial Setup when PDF is opened ---
// Hide controls to start with, they'll become visible when game_init() is called
set_controls_visibility(false);

// Zoom to fit the page in the viewer (on Firefox and other compatible viewers)
app.execMenuItem("FitPage");

endstream
endobj


18 0 obj
<<
  /JS 43 0 R
  /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream

endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

# --- PDF Object Templates ---
PLAYING_FIELD_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      0.8
    ]
    /BC [
      0 0 0
    ]
  >>
  /Border [ 2 2 1 ]  # Border width of 1 points, with 2-unit rounded corners
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (playing_field)
  /Type /Annot
>>
endobj
"""

PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      ###COLOR_RGB###
    ]
    /BC [
      0.7 0.7 0.7
    ]
  >>
  /Border [ 0 0 0.5 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###_###COLOR_NAME###)
  /Type /Annot
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
###BUTTON_COLOR### rg
0 0 ###WIDTH### ###HEIGHT### re
f
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 12 Tf
0 g
10 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

BUTTON_OBJ = """
###IDX### obj
<<
  /A <<
      /JS ###SCRIPT_IDX### R
      /S /JavaScript
    >>
  /AP <<
    /N ###AP_IDX### R
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
        0.75 0.75 0.75
    ]
    /CA (###LABEL###)
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
    /AA <<
        /K <<
            /JS ###SCRIPT_IDX### R
            /S /JavaScript
        >>
    >>
    /DA (/Helvetica ###FONT_SIZE### Tf 0 g)
    /F 4
    /FT /Tx
    /MK <<
        /BC [ 0 0 0 ]
        /BG [ ###BG_COLOR### ]
    >>
    /MaxLen 0
    /P 16 0 R
    /Rect [
        ###RECT###
    ]
    /Subtype /Widget
    /T (###NAME###)
    /V (###LABEL###)
    /Type /Annot
>>
endobj
"""

STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

# --- Configuration for Grid and UI ---
PX_SIZE = 10
GRID_WIDTH = 40
GRID_HEIGHT = 50
# GRID_OFF_X = 80
# GRID_OFF_Y = 200
# A4 dimensions are approx 595 x 842 points
# Let's target a central grid and adjust offsets accordingly
PAGE_WIDTH = 612  # Standard PDF A4 width
PAGE_HEIGHT = 792  # Standard PDF A4 height

GRID_DRAW_WIDTH = GRID_WIDTH * PX_SIZE
GRID_DRAW_HEIGHT = GRID_HEIGHT * PX_SIZE

GRID_OFF_X = (PAGE_WIDTH - GRID_DRAW_WIDTH) / 2
GRID_OFF_Y = PAGE_HEIGHT - GRID_DRAW_HEIGHT - 80

# Define colors for pixel variations
COLOR_MAP = {
    "PLAYER": "0.0 0.7 0.0",  # Green
    "BULLET": "1.0 0.6 0.0",  # Orange
    "ENEMY": "1.0 0.0 0.0",  # Red
    "BLAST": "1.0 1.0 0.0",  # Yellow
    "OFF": "0.0 0.0 0.0",  # Black (default hidden state)
}

# Define blast duration in milliseconds (for JS)
BLAST_DURATION = 100

# --- Global Variables for PDF Generation ---
fields_text = ""  # Accumulates the PDF object definitions for fields
field_indexes = []  # List of object indexes for all fields
obj_idx_ctr = 50  # Counter for unique PDF object IDs


# --- Helper Functions for Adding PDF Objects ---
def add_field(field):
    """Adds a generated PDF field object to the fields_text and updates index."""
    global fields_text, field_indexes, obj_idx_ctr
    fields_text += field
    field_indexes.append(obj_idx_ctr)
    obj_idx_ctr += 1


def add_button(label, name, x, y, width, height, js, button_color_rgb="0.75 0.75 0.75"):
    """Adds a button field with associated JavaScript action."""
    global obj_idx_ctr
    script = STREAM_OBJ  # Template for the JavaScript action stream
    script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
    script = script.replace("###CONTENT###", js)
    add_field(script)

    ap_stream = BUTTON_AP_STREAM  # Template for the button's appearance stream
    ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
    ap_stream = ap_stream.replace("###TEXT###", label)
    ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
    ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
    ap_stream = ap_stream.replace(
        "###BUTTON_COLOR###", button_color_rgb
    )  # Set the color in AP stream
    add_field(ap_stream)

    button = BUTTON_OBJ  # Template for the button widget object
    button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
    button = button.replace(
        "###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0"
    )  # Links to JS stream
    button = button.replace(
        "###AP_IDX###", f"{obj_idx_ctr-1} 0"
    )  # Links to appearance stream
    button = button.replace("###LABEL###", label)
    button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
    button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    add_field(button)


def add_text(
    label,
    name,
    x,
    y,
    width,
    height,
    js="",
    read_only=False,
    bg_color="1 1 1",
    font_size=12,
):
    """Adds a text input field with associated JavaScript action (for keyboard input) or static text."""
    global obj_idx_ctr
    script_idx = "null"  # Default for no JS
    if js:
        script = STREAM_OBJ  # Template for the JavaScript action stream
        script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
        script = script.replace("###CONTENT###", js)
        add_field(script)
        script_idx = f"{obj_idx_ctr-1} 0"  # Links to JS stream

    text = TEXT_OBJ  # Template for the text widget object
    text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
    text = text.replace("###SCRIPT_IDX###", script_idx)
    text = text.replace("###LABEL###", label.replace("\n", "\\n"))  # Handle newlines
    text = text.replace("###NAME###", name)
    text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    text = text.replace("###BG_COLOR###", bg_color)
    text = text.replace("###FONT_SIZE###", str(font_size))

    if read_only:
        text = text.replace("<<", "<<\n    /Ff 1")

    add_field(text)


# --- Generate Grid Pixels ---
# Playing field outline (a simple border for the grid)
playing_field = PLAYING_FIELD_OBJ
playing_field = playing_field.replace("###IDX###", f"{obj_idx_ctr} 0")
playing_field = playing_field.replace(
    "###RECT###",
    f"{GRID_OFF_X} {GRID_OFF_Y} {GRID_OFF_X+GRID_WIDTH*PX_SIZE} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE}",
)
add_field(playing_field)

# Individual pixel fields for the grid (multiple for each color variation)
for x in range(GRID_WIDTH):
    for y_game in range(GRID_HEIGHT):
        # PDF Y-coordinates are inverted, so map game_y to pdf_y for field naming
        y_pdf = GRID_HEIGHT - 1 - y_game
        for color_name, color_rgb in COLOR_MAP.items():
            pixel = PIXEL_OBJ
            pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
            pixel = pixel.replace("###COLOR_RGB###", color_rgb)
            # Position each pixel within the grid offset
            pixel = pixel.replace(
                "###RECT###",
                f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y_pdf*PX_SIZE} {GRID_OFF_X+x*PX_SIZE+PX_SIZE} {GRID_OFF_Y+y_pdf*PX_SIZE+PX_SIZE}",
            )
            pixel = pixel.replace("###X###", f"{x}")
            pixel = pixel.replace(
                "###Y###", f"{y_pdf}"
            )  # Use PDF Y for field naming consistent with rect
            pixel = pixel.replace("###COLOR_NAME###", color_name)
            add_field(pixel)

# --- Generate UI Buttons and Text Fields ---
# Movement buttons (positioned like a keyboard layout)
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 45
BUTTON_SPACING = 4

# Calculate positions for the control block
# We'll place the controls centered below the grid
controls_block_width = (BUTTON_WIDTH * 3) + (BUTTON_SPACING * 2)  # WASD block
controls_block_start_x = GRID_OFF_X + (GRID_DRAW_WIDTH / 2) - (controls_block_width / 2)

# Y-coordinates for the bottom row of buttons (LEFT, DOWN, RIGHT)
BUTTON_BOTTOM_ROW_Y = GRID_OFF_Y - 150  # Position below the grid

# X-coordinates for the movement buttons
X_LEFT_BUTTON = controls_block_start_x
X_DOWN_BUTTON = X_LEFT_BUTTON + BUTTON_WIDTH + BUTTON_SPACING
X_RIGHT_BUTTON = X_DOWN_BUTTON + BUTTON_WIDTH + BUTTON_SPACING

# UP button's Y-coordinate (above the DOWN button)
Y_UP_BUTTON = BUTTON_BOTTOM_ROW_Y + BUTTON_HEIGHT + BUTTON_SPACING

add_button(
    "UP",
    "B_up",
    X_DOWN_BUTTON,
    Y_UP_BUTTON,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "move_player(0, -1);",
    "0.75 0.75 0.75",
)

add_button(
    "LEFT",
    "B_left",
    X_LEFT_BUTTON,
    BUTTON_BOTTOM_ROW_Y,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "move_player(-1, 0);",
    "0.75 0.75 0.75",
)

add_button(
    "DOWN",
    "B_down",
    X_DOWN_BUTTON,
    BUTTON_BOTTOM_ROW_Y,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "move_player(0, 1);",
    "0.75 0.75 0.75",
)

add_button(
    "RIGHT",
    "B_right",
    X_RIGHT_BUTTON,
    BUTTON_BOTTOM_ROW_Y,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "move_player(1, 0);",
    "0.75 0.75 0.75",
)

# Fire Button - placed to the right of the movement buttons
FIRE_BUTTON_WIDTH = 80
FIRE_BUTTON_X = X_RIGHT_BUTTON + BUTTON_WIDTH + BUTTON_SPACING * 2
FIRE_BUTTON_Y = BUTTON_BOTTOM_ROW_Y
add_button(
    "FIRE!",
    "B_fire",
    FIRE_BUTTON_X,
    FIRE_BUTTON_Y,
    FIRE_BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "fire_bullet();",
    "1.0 0.4 0.2",
)

# Start Game button (its position can remain relatively central to the grid)
# Place it slightly below the grid, above the other controls
add_button(
    "Start Game!",
    "B_start",
    GRID_OFF_X + (GRID_DRAW_WIDTH / 2) - 50,
    GRID_OFF_Y + (GRID_DRAW_HEIGHT / 2),
    100,
    40,
    "game_init();",
)

# Text input for keyboard controls
# Position it aligned with the control block, slightly above the key map text
TEXT_INPUT_FIELD_HEIGHT = 25
TEXT_INPUT_Y = BUTTON_BOTTOM_ROW_Y - 30 - TEXT_INPUT_FIELD_HEIGHT
add_text(
    "type wasd to move",  # Keep label empty as instructions are separate
    "T_input",
    controls_block_start_x,
    TEXT_INPUT_Y,
    controls_block_width + FIRE_BUTTON_WIDTH + BUTTON_SPACING * 2,
    TEXT_INPUT_FIELD_HEIGHT,
    "handle_input(event);",
    bg_color="0.8 0.9 1.0",
)

# --- Title ---
TITLE_HEIGHT = 25
TITLE_WIDTH = 180
TITLE_X = (PAGE_WIDTH - TITLE_WIDTH) / 2
TITLE_X_1 = GRID_OFF_X
TITLE_WIDTH_1 = GRID_DRAW_WIDTH
TITLE_Y = GRID_OFF_Y + GRID_DRAW_HEIGHT + 20

add_text(
    "SPACE INVADERS",
    "T_title_main",
    TITLE_X,
    TITLE_Y,
    TITLE_WIDTH,
    TITLE_HEIGHT,
    "",
    read_only=True,
    bg_color="0.7 0.7 1.0",
    font_size=20,
)

# positioned below the title
GAP = 15
add_text(
    "GitHub: https://github.com/Harshit-Dhanwalkar/pdf-spaceinvader",
    "T_title_github",
    TITLE_X_1,
    TITLE_Y - GAP - 2,
    TITLE_WIDTH_1,
    GAP,
    "",
    read_only=True,
    bg_color="0.8 0.8 1.0",
    font_size=8,
)

# --- Final PDF Assembly ---
# Replace placeholders in the main PDF template
filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace(
    "###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes])
)
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")
filled_pdf = filled_pdf.replace("BLAST_DURATION", f"{BLAST_DURATION}")

# --- Write to PDF File ---
# Open a file in write mode and save the generated PDF content
pdffile = open("movable_square.pdf", "w")
pdffile.write(filled_pdf)
pdffile.close()

print("PDF game 'movable_square.pdf' generated successfully!")
