

# Space-Sim

A Python project to simulate the gravitational interactions between celestial bodies, specifically the Sun, Earth, and Moon, using the Pygame library. The simulation accurately models the orbits of these bodies, showing how they influence each other's motion through gravitational forces.

## Features

- **Realistic Gravitational Interactions:** The simulation takes into account the gravitational forces between the Sun, Earth, and Moon, allowing for realistic orbital dynamics.
- **Pygame Visualization:** The project uses Pygame to visualize the simulation in real-time, with the option to display or hide the orbits of the celestial bodies.
- **Dynamic Simulation:** The celestial bodies move according to the laws of physics, with their positions and velocities continuously updated based on gravitational forces.

## Project Structure

Here is an overview of the files and directories that should be included in this project:

```
Space-Sim/
│
├── README.md                # Project documentation (this file)
├── main.py                  # Main script to run the simulation
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignore file to exclude unnecessary files from the repository
├── LICENSE                  # License for the project (MIT License)
└── assets/                  # Directory for any additional assets like images or fonts
    └── placeholder.txt      # Placeholder file (optional), can be deleted when assets are added
```

### Detailed Description

- **`README.md`:**  
  This file. Provides an overview of the project, instructions on how to set up and run the simulation, and details about the project structure and files.

- **`main.py`:**  
  The main Python script containing the simulation logic. This script defines the `HeavenlyBody` class and the main loop that runs the simulation.

- **`requirements.txt`:**  
  Lists all the Python dependencies needed to run the project. For this project, it should contain:
  
  ```
  pygame==2.6.0
  ```
  
  To install the dependencies, users can run:
  
  ```bash
  pip install -r requirements.txt
  ```

- **`.gitignore`:**  
  A file that tells Git which files and directories to ignore in the repository. Typically, it would include:

  ```
  __pycache__/
  *.pyc
  .DS_Store
  .vscode/
  .idea/
  ```

- **`LICENSE`:**  
  The MIT License file that provides the terms under which the project's code can be used.

- **`assets/`:**  
  A directory to store any additional assets like images, sounds, or custom fonts that may be used in the project. The `placeholder.txt` file is optional and can be removed once you add real assets to the directory.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/HeavenlyBodiesSimulation.git
   cd HeavenlyBodiesSimulation
   ```

2. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the simulation:**

   ```bash
   python main.py
   ```

### Controls

- **`O` Key:** Toggle the display of the orbits of the celestial bodies.
- **`Q` Key:** Quit the simulation.

## How It Works

The simulation calculates the gravitational force between each pair of celestial bodies using Newton's law of universal gravitation:

\[ F = \frac{G \cdot m_1 \cdot m_2}{r^2} \]

Where:
- \( F \) is the gravitational force between the bodies.
- \( G \) is the gravitational constant.
- \( m_1 \) and \( m_2 \) are the masses of the two bodies.
- \( r \) is the distance between the centers of the two bodies.

These forces are used to update the velocity and position of each body at every time step. The Pygame library is used to render the positions and orbits of the bodies on the screen.

## Customization

You can easily add more celestial bodies to the simulation by creating additional instances of the `HeavenlyBody` class and adding them to the `bodies` list in the `main.py` file.

Example:

```python
mars = HeavenlyBody("Mars", 6.39e23, 2.279e11, 0, 6, RED)
mars.y_velocity = -24.077e3
bodies.append(mars)
```

## Contributing

If you would like to contribute to this project, please fork the repository, create a new branch for your feature or bugfix, and submit a pull request. All contributions are welcome!

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

This project was inspired by the fascinating dynamics of celestial mechanics and aims to provide an educational and visual tool for understanding these complex interactions.
