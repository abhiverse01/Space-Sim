# rocket_simulation.py

import pygame
import pygame_gui
import math
import sys

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
M_EARTH = 5.972e24  # Mass of Earth (kg)
R_EARTH = 6.371e6   # Radius of Earth (m)
AIR_DENSITY_SEA_LEVEL = 1.225  # kg/m^3
SCALE = 1e-5  # Scale for rendering (pixels per meter)
TIMESTEP = 0.1  # Simulation time step (seconds)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (130, 130, 130)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Rocket parameters
class Rocket:
    def __init__(self, mass, fuel_mass, position, velocity, angle):
        self.mass = mass  # Dry mass (kg)
        self.fuel_mass = fuel_mass  # Fuel mass (kg)
        self.total_mass = self.mass + self.fuel_mass  # Total mass (kg)
        self.position = position  # Position vector (x, y) in meters
        self.velocity = velocity  # Velocity vector (vx, vy) in m/s
        self.angle = angle  # Launch angle in degrees
        self.thrust = 0  # Thrust force (N)
        self.thrusting = True  # Whether the rocket engine is on
        self.exhaust_velocity = 3000  # Exhaust velocity (m/s)
        self.drag_coefficient = 0.5  # Dimensionless
        self.cross_sectional_area = 10  # Cross-sectional area (m^2)
        self.acceleration = [0, 0]  # Acceleration vector (ax, ay) in m/s^2
        self.path = []  # Trajectory path for rendering

    def update_rk4(self, dt, environment):
        # State vector: [x, y, vx, vy, total_mass, fuel_mass]
        state = [self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.total_mass, self.fuel_mass]

        # Define the derivatives function
        def derivatives(state):
            x, y, vx, vy, total_mass, fuel_mass = state
            position = [x, y]
            velocity = [vx, vy]

            # Compute forces
            # Gravitational force
            distance = math.hypot(position[0], position[1])
            fg_magnitude = G * M_EARTH * total_mass / distance**2
            fg_x = -fg_magnitude * (position[0] / distance)
            fg_y = -fg_magnitude * (position[1] / distance)

            # Drag force
            altitude = distance - R_EARTH
            air_density = environment.get_air_density(altitude)
            speed = math.hypot(velocity[0], velocity[1])
            if speed == 0:
                fd_x = fd_y = 0
            else:
                drag_magnitude = 0.5 * air_density * speed**2 * self.drag_coefficient * self.cross_sectional_area
                fd_x = -drag_magnitude * (velocity[0] / speed)
                fd_y = -drag_magnitude * (velocity[1] / speed)

            # Thrust force
            if self.thrusting and fuel_mass > 0:
                thrust_force = self.thrust
                fuel_consumption_rate = self.thrust / self.exhaust_velocity
                # Mass rate of change
                d_mass = -fuel_consumption_rate
            else:
                thrust_force = 0
                fuel_consumption_rate = 0
                d_mass = 0
            thrust_angle = math.radians(self.angle)
            ft_x = thrust_force * math.cos(thrust_angle)
            ft_y = thrust_force * math.sin(thrust_angle)

            # Total forces
            total_fx = fg_x + fd_x + ft_x
            total_fy = fg_y + fd_y + ft_y

            # Acceleration
            ax = total_fx / total_mass
            ay = total_fy / total_mass

            return [vx, vy, ax, ay, d_mass, d_mass]

        # RK4 integration
        k1 = derivatives(state)
        state_k2 = [state[i] + 0.5 * dt * k1[i] for i in range(6)]
        k2 = derivatives(state_k2)
        state_k3 = [state[i] + 0.5 * dt * k2[i] for i in range(6)]
        k3 = derivatives(state_k3)
        state_k4 = [state[i] + dt * k3[i] for i in range(6)]
        k4 = derivatives(state_k4)

        # Update state
        new_state = [state[i] + (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) for i in range(6)]

        # Update self
        self.position = [new_state[0], new_state[1]]
        self.velocity = [new_state[2], new_state[3]]
        self.total_mass = new_state[4]
        self.fuel_mass = new_state[5]

        # Ensure mass doesn't go negative
        if self.fuel_mass < 0:
            self.fuel_mass = 0
            self.total_mass = self.mass

        # Update thrusting status
        if self.fuel_mass <= 0:
            self.thrusting = False
            self.thrust = 0

        # Append to path for rendering
        self.path.append((self.position[0], self.position[1]))
        if len(self.path) > 5000:
            self.path.pop(0)

class Atmosphere:
    def __init__(self):
        self.scale_height = 8500  # Scale height for Earth's atmosphere (m)

    def get_air_density(self, altitude):
        # Exponential decrease of air density with altitude
        if altitude < 0:
            altitude = 0
        rho = AIR_DENSITY_SEA_LEVEL * math.exp(-altitude / self.scale_height)
        return rho

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Rocket Launch Simulation")
    clock = pygame.time.Clock()

    # Font for displaying text
    font = pygame.font.SysFont('Arial', 14)

    # Initialize pygame_gui
    manager = pygame_gui.UIManager((width, height))

    # Create GUI elements
    dry_mass_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 150), (100, 30)), manager=manager)
    dry_mass_input.set_text('50000')  # Default value

    fuel_mass_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 200), (100, 30)), manager=manager)
    fuel_mass_input.set_text('150000')

    thrust_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 250), (100, 30)), manager=manager)
    thrust_input.set_text('3500000')

    angle_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 300), (100, 30)), manager=manager)
    angle_input.set_text('90')

    start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 350), (100, 50)), text='Start', manager=manager)

    # Labels
    dry_mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 150), (100, 30)), text='Dry Mass (kg):', manager=manager)
    fuel_mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 200), (100, 30)), text='Fuel Mass (kg):', manager=manager)
    thrust_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 250), (100, 30)), text='Thrust (N):', manager=manager)
    angle_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 300), (100, 30)), text='Launch Angle (°):', manager=manager)

    # Simulation variables
    run = True
    paused = False
    zoom = 1e-2  # Initial zoom level
    offset_x = width / 2
    offset_y = height

    # Simulation state: 'setup' or 'simulation'
    state = 'setup'
    time_since_last_frame = 0.0

    # Initialize the atmosphere
    atmosphere = Atmosphere()

    while run:
        time_delta = clock.tick(60) / 1000.0
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if state == 'setup':
                manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        # Get input values
                        try:
                            dry_mass = float(dry_mass_input.get_text())
                            fuel_mass = float(fuel_mass_input.get_text())
                            thrust = float(thrust_input.get_text())
                            angle = float(angle_input.get_text())
                        except ValueError:
                            # Display error message
                            error_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 400), (200, 30)), text='Invalid input!', manager=manager)
                            continue

                        # Initialize the rocket
                        rocket = Rocket(
                            mass=dry_mass,  # Dry mass in kg
                            fuel_mass=fuel_mass,  # Fuel mass in kg
                            position=[0, R_EARTH],  # Starting at the surface of the Earth
                            velocity=[0, 0],  # Initial velocity
                            angle=angle  # Launch angle in degrees
                        )
                        rocket.thrust = thrust
                        simulation_time = 0.0  # Simulation time in seconds
                        state = 'simulation'

                        # Hide GUI elements
                        dry_mass_input.kill()
                        fuel_mass_input.kill()
                        thrust_input.kill()
                        angle_input.kill()
                        start_button.kill()
                        dry_mass_label.kill()
                        fuel_mass_label.kill()
                        thrust_label.kill()
                        angle_label.kill()
                        if 'error_label' in locals():
                            error_label.kill()

            elif state == 'simulation':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        run = False
                    elif event.key == pygame.K_UP:
                        zoom *= 1.2
                    elif event.key == pygame.K_DOWN:
                        zoom /= 1.2
                manager.process_events(event)

        if state == 'setup':
            manager.update(time_delta)
            manager.draw_ui(screen)
            # Display title
            title_label = font.render('Rocket Launch Simulation Setup', True, WHITE)
            screen.blit(title_label, (width // 2 - title_label.get_width() // 2, 50))
        elif state == 'simulation':
            if not paused:
                # Update simulation time
                simulation_time += TIMESTEP

                # Update simulation
                rocket.update_rk4(TIMESTEP, atmosphere)

                # Check for collision with Earth
                distance_from_center = math.hypot(rocket.position[0], rocket.position[1])
                if distance_from_center <= R_EARTH:
                    paused = True
                    crash_label = font.render('The rocket has crashed back to Earth!', True, RED)
                    screen.blit(crash_label, (width // 2 - crash_label.get_width() // 2, height // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    run = False
                    continue

            # Drawing the Earth
            earth_radius_pixels = R_EARTH * SCALE * zoom
            pygame.draw.circle(screen, BLUE, (int(offset_x), int(offset_y)), max(int(earth_radius_pixels), 1))

            # Drawing the rocket trajectory
            if len(rocket.path) > 1:
                transformed_path = []
                for pos in rocket.path:
                    x = pos[0] * SCALE * zoom + offset_x
                    y = -pos[1] * SCALE * zoom + offset_y
                    transformed_path.append((x, y))
                pygame.draw.lines(screen, RED, False, transformed_path, 2)

            # Drawing the rocket
            rocket_x = rocket.position[0] * SCALE * zoom + offset_x
            rocket_y = -rocket.position[1] * SCALE * zoom + offset_y
            pygame.draw.circle(screen, GREEN, (int(rocket_x), int(rocket_y)), 5)

            # Displaying information
            altitude = math.hypot(rocket.position[0], rocket.position[1]) - R_EARTH
            speed = math.hypot(rocket.velocity[0], rocket.velocity[1])
            info_lines = [
                f"Time: {simulation_time:.1f} s",
                f"Altitude: {altitude / 1000:.1f} km",
                f"Speed: {speed / 1000:.1f} km/s",
                f"Fuel Mass: {rocket.fuel_mass:.1f} kg",
                f"Thrust: {rocket.thrust:.1f} N",
                "Controls:",
                "  SPACE: Pause/Resume",
                "  UP/DOWN: Zoom In/Out",
                "  ESC: Quit"
            ]
            y_offset = 10
            for line in info_lines:
                text = font.render(line, True, WHITE)
                screen.blit(text, (10, y_offset))
                y_offset += 20

            manager.update(time_delta)
            manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
