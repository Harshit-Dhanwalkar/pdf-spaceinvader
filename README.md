# PDF Space Invaders

A classic arcade game reimagined! This project demonstrates how to create a playable **Space Invaders** clone entirely within a PDF file, leveraging PDF form fields and embedded JavaScript. Move your spaceship and fire at oncoming invaders, all powered by the surprising interactive capabilities of the PDF format.

---

## Features

- **Pure PDF Gameplay:** The entire game logic and rendering run directly within the PDF file using embedded JavaScript.
- **Form Field Graphics:** The game "pixels" are dynamically updated PDF form fields, changing their visibility and color to render the game state.
- **Browser Compatibility:** Playable in modern PDF viewers, including popular browsers like Chrome, Edge, and Firefox, as well as dedicated PDF readers like Adobe Acrobat Reader.
- **Simple Controls:** Move with WASD or arrow keys and fire with Spacebar or '/'.

---

## How to Play

1.  **Download the PDF:**
    Download the `movable_square.pdf` file directly from this repository or git clone.
    [**Download `movable_square.pdf`**](https://github.com/Harshit-Dhanwalkar/pdf-space-invader/raw/main/movable_square.pdf) (Right-click and "Save link as...")

2.  **Open the PDF:**
    Open `movable_square.pdf` in a modern PDF viewer.

    - **Recommended:** Google Chrome, Microsoft Edge, Mozilla Firefox (built-in PDF viewer).
    - **Desktop:** Adobe Acrobat Reader.
    - _Note: Performance and full interactivity may vary across different PDF viewers._

3.  **Start the Game:**
    Click the "Start Game!" button within the PDF to begin.

4.  **Controls:**
    - **Move:** `W` (Up), `S` (Down), `A` (Left), `D` (Right) or **Arrow Keys**.
    - **Fire:** `Spacebar` or `/` (forward slash).
    - Input your commands in the text field provided below the game grid.

---

## How to Build It Yourself

This project uses Python to programmatically generate the PDF file.

### Prerequisites

- **Python 3** installed on your system.

### Steps

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Harshit-Dhanwalkar/pdf-spaceinvader.git
    cd pdf-spaceinvader
    ```

2.  **Generate the PDF Game:**
    Run the Python script to create the PDF file:

    ```bash
    python3 generate.py
    ```

    This command will generate `movable_square.pdf` in your current directory.

3.  **Open and Play:**
    Open the newly generated `movable_square.pdf` in your browser or a PDF reader and enjoy the game!

---

## Contributing

Feel free to open issues or submit pull requests if you have ideas for improvements, bug fixes, or new features.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgements

- Inspired by the ingenious work on [DoomPDF](https://github.com/ading2210/doompdf) by ading2210.

* Inspired by the creative approach of [pdf-tetris](https://github.com/gregnb/pdf-tetris) by gregnb.
