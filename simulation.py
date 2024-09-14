# simulation_.py

import pygame
import math

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
TIMESTEP = 60    # One minute per simulation step (seconds)
SCALE = 250 / (1.5e11)  # Scale: 1.5e11 meters (1 AU) = 250 pixels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
GREY = (200, 200, 200)

class HeavenlyBody:
    """
    Represents a celestial body with mass, position, velocity, and methods to
    calculate gravitational forces and update positions.
    """
    def __init__(self, name, mass, x, y, radius, color):
        self.name = name
        self.mass = mass
        self.x = x  # Position in meters
        self.y = y
        self.radius = radius  # Radius in pixels for rendering
        self.color = color
        self.x_velocity = 0  # Velocity in m/s
        self.y_velocity = 0
        self.orbit = []
        self.is_sun = False  # Flag to identify the sun

    def draw(self, screen, zoom, offset_x, offset_y, font, show_orbit=True):
        """
        Draws the celestial body and its orbit on the screen.
        """
        # Convert position to pixels and apply zoom and offset
        x = (self.x * SCALE * zoom) + screen.get_width() / 2 + offset_x
        y = (self.y * SCALE * zoom) + screen.get_height() / 2 + offset_y

        # Draw the orbit path
        if show_orbit and len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px = (point[0] * SCALE * zoom) + screen.get_width() / 2 + offset_x
                py = (point[1] * SCALE * zoom) + screen.get_height() / 2 + offset_y
                updated_points.append((px, py))
            if len(updated_points) > 1:
                pygame.draw.lines(screen, self.color, False, updated_points, 1)

        # Draw the celestial body
        pygame.draw.circle(screen, self.color, (int(x), int(y)), max(int(self.radius * zoom), 1))

        # Draw the name of the body if zoomed in sufficiently
        if zoom > 0.5:
            name_label = font.render(self.name, True, WHITE)
            screen.blit(name_label, (x - name_label.get_width() / 2, y - name_label.get_height() / 2))

    def calculate_gravitational_force(self, other):
        """
        Calculates the gravitational force exerted by another celestial body.
        """
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.hypot(distance_x, distance_y)

        if distance == 0:
            raise ValueError(f"Collision between {self.name} and {other.name}")

        force = G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, bodies):
        """
        Updates the celestial body's velocity and position using the Velocity Verlet method.
        """
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue
            try:
                fx, fy = self.calculate_gravitational_force(body)
                total_fx += fx
                total_fy += fy
            except ValueError as e:
                print(e)
                continue

        # Calculate acceleration
        ax = total_fx / self.mass
        ay = total_fy / self.mass

        # Update velocities (half step)
        self.x_velocity += ax * TIMESTEP / 2
        self.y_velocity += ay * TIMESTEP / 2

        # Update positions
        self.x += self.x_velocity * TIMESTEP
        self.y += self.y_velocity * TIMESTEP

        # Update velocities (another half step)
        self.x_velocity += ax * TIMESTEP / 2
        self.y_velocity += ay * TIMESTEP / 2

        # Append current position to orbit
        self.orbit.append((self.x, self.y))
        if len(self.orbit) > 5000:
            self.orbit.pop(0)

def create_celestial_bodies():
    """
    Initializes the Sun, Earth, and Moon with accurate positions and velocities.
    """
    # Sun
    sun = HeavenlyBody("Sun", 1.98847e30, 0, 0, 30, YELLOW)
    sun.is_sun = True  # Identify the sun

    # Earth
    earth_distance = 1.496e11  # Average distance from Sun to Earth in meters
    earth_orbital_speed = 29.78e3  # Average orbital speed of Earth in m/s
    earth = HeavenlyBody("Earth", 5.972e24, -earth_distance, 0, 16, BLUE)
    earth.y_velocity = earth_orbital_speed

    # Moon
    moon_distance = 3.844e8  # Average distance from Earth to Moon in meters
    moon_orbital_speed = 1.022e3  # Average orbital speed of Moon in m/s
    moon = HeavenlyBody("Moon", 7.34767309e22, -earth_distance - moon_distance, 0, 6, GREY)
    moon.y_velocity = earth.y_velocity + moon_orbital_speed

    return [sun, earth, moon]

def main():
    """
    Main function to run the simulation.
    """
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Earth-Moon-Sun Simulation")

    bodies = create_celestial_bodies()

    clock = pygame.time.Clock()
    run = True
    show_orbit = True

    # Set up font for labels
    font = pygame.font.SysFont('Arial', 14)

    # Zoom and pan variables
    zoom_level = 1.0
    offset_x = 0
    offset_y = 0
    is_dragging = False
    drag_start_pos = (0, 0)

    # Simulation speed control
    simulation_speed = 1  # Multiplier for TIMESTEP

    while run:
        clock.tick(60)  # Limit to 60 FPS
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    show_orbit = not show_orbit
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    simulation_speed *= 2
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    simulation_speed = max(simulation_speed / 2, 0.125)
                elif event.key == pygame.K_SPACE:
                    simulation_speed = 0 if simulation_speed != 0 else 1
                elif event.key == pygame.K_r:
                    bodies = create_celestial_bodies()
                    offset_x, offset_y = 0, 0
                    zoom_level = 1.0
                    simulation_speed = 1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    zoom_level *= 1.1
                elif event.button == 5:  # Scroll down
                    zoom_level /= 1.1
                elif event.button == 1:  # Left mouse button
                    is_dragging = True
                    drag_start_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = event.pos[0] - drag_start_pos[0]
                    dy = event.pos[1] - drag_start_pos[1]
                    offset_x += dx
                    offset_y += dy
                    drag_start_pos = event.pos

        # Update and draw celestial bodies
        if simulation_speed != 0:
            for body in bodies:
                body.update_position(bodies)

        for body in bodies:
            body.draw(screen, zoom_level, offset_x, offset_y, font, show_orbit)

        # Draw labels and info
        info_y_offset = 10
        info_lines = [
            f"Simulation Speed: {simulation_speed}x",
            f"Zoom Level: {zoom_level:.2f}",
            "Controls:",
            "  + / - : Increase/Decrease Simulation Speed",
            "  Mouse Wheel: Zoom In/Out",
            "  Drag Mouse: Pan View",
            "  O: Toggle Orbits",
            "  Space: Pause/Resume Simulation",
            "  R: Reset Simulation"
        ]

        for line in info_lines:
            label = font.render(line, True, WHITE)
            screen.blit(label, (10, info_y_offset))
            info_y_offset += 18

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
