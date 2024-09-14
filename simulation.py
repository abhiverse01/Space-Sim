# simulation.py

import pygame
import math

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
TIMESTEP = 3600  # One hour per simulation step (seconds)
SCALE = 2 / (3e11)  # Scale for rendering purposes (meters per pixel)

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

    def draw(self, screen, show_orbit=True):
        """
        Draws the celestial body and its orbit on the screen.
        """
        # Convert position to pixels
        x = self.x * SCALE + screen.get_width() / 2
        y = self.y * SCALE + screen.get_height() / 2

        # Draw the orbit path
        if show_orbit and len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px, py = point
                px = px * SCALE + screen.get_width() / 2
                py = py * SCALE + screen.get_height() / 2
                updated_points.append((px, py))
            pygame.draw.lines(screen, self.color, False, updated_points, 1)

        # Draw the celestial body
        pygame.draw.circle(screen, self.color, (int(x), int(y)), self.radius)

    def calculate_gravitational_force(self, other):
        """
        Calculates the gravitational force exerted by another celestial body.
        """
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.hypot(distance_x, distance_y)

        if distance == 0:
            return 0, 0  # Avoid division by zero

        force = G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, bodies):
        """
        Updates the celestial body's velocity and position based on gravitational forces.
        """
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue
            fx, fy = self.calculate_gravitational_force(body)
            total_fx += fx
            total_fy += fy

        # Update velocities based on acceleration
        self.x_velocity += total_fx / self.mass * TIMESTEP
        self.y_velocity += total_fy / self.mass * TIMESTEP

        # Update positions based on velocity
        self.x += self.x_velocity * TIMESTEP
        self.y += self.y_velocity * TIMESTEP

        # Append current position to orbit
        self.orbit.append((self.x, self.y))
        if len(self.orbit) > 2000:
            self.orbit.pop(0)

def create_celestial_bodies():
    """
    Initializes the Sun, Earth, and Moon with accurate positions and velocities.
    """
    # Sun
    sun = HeavenlyBody("Sun", 1.98847e30, 0, 0, 16, YELLOW)

    # Earth
    earth_distance = 1.496e11  # Average distance from Sun to Earth in meters
    earth_orbital_speed = 29.78e3  # Average orbital speed of Earth in m/s
    earth = HeavenlyBody("Earth", 5.972e24, -earth_distance, 0, 8, BLUE)
    earth.y_velocity = earth_orbital_speed

    # Moon
    moon_distance = 3.844e8  # Average distance from Earth to Moon in meters
    moon_orbital_speed = 1.022e3  # Average orbital speed of Moon in m/s
    moon = HeavenlyBody("Moon", 7.34767309e22, -earth_distance - moon_distance, 0, 4, GREY)
    moon.y_velocity = earth.y_velocity + moon_orbital_speed

    return [sun, earth, moon]

def main():
    """
    Main function to run the simulation.
    """
    pygame.init()
    width, height = 800, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Earth-Moon-Sun Simulation")

    bodies = create_celestial_bodies()

    clock = pygame.time.Clock()
    run = True
    show_orbit = True

    # Set up font for labels
    font = pygame.font.SysFont('Arial', 14)

    while run:
        clock.tick(60)  # Limit to 60 FPS
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    show_orbit = not show_orbit

        # Update and draw celestial bodies
        for body in bodies:
            body.update_position(bodies)
            body.draw(screen, show_orbit)

        # Draw labels
        label_y_offset = 10
        for body in bodies:
            label = font.render(f"{body.name}", True, body.color)
            screen.blit(label, (10, label_y_offset))
            label_y_offset += 20

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
