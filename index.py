# simulation_enhanced.py

import pygame
import math
import sys

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
TIMESTEP = 60    # One minute per simulation step (seconds)
SCALE = 250 / (1.5e11)  # Scale: 1.5e11 meters (1 AU) = 250 pixels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
GREY = (130, 130, 130)
RED = (188, 39, 50)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)

class HeavenlyBody:
    """
    Represents a celestial body with mass, position, velocity, and methods to
    calculate gravitational forces and update positions.
    """
    AU = 1.496e11  # Astronomical unit in meters

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
        body_radius = max(int(self.radius * zoom), 1)
        pygame.draw.circle(screen, self.color, (int(x), int(y)), body_radius)

        # Draw the name of the body if zoomed in sufficiently
        if zoom > 0.5:
            name_label = font.render(self.name, True, WHITE)
            screen.blit(name_label, (x - name_label.get_width() / 2, y - body_radius - name_label.get_height()))

    def calculate_gravitational_force(self, other):
        """
        Calculates the gravitational force exerted by another celestial body.
        """
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.hypot(distance_x, distance_y)

        if distance == 0:
            return 0, 0  # Ignore self-interaction or collision

        force = G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, bodies, timestep):
        """
        Updates the celestial body's velocity and position using the Velocity Verlet method.
        """
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue
            fx, fy = self.calculate_gravitational_force(body)
            total_fx += fx
            total_fy += fy

        # Calculate acceleration
        ax = total_fx / self.mass
        ay = total_fy / self.mass

        # Update velocities (half step)
        self.x_velocity += ax * timestep / 2
        self.y_velocity += ay * timestep / 2

        # Update positions
        self.x += self.x_velocity * timestep
        self.y += self.y_velocity * timestep

        # Update velocities (another half step)
        self.x_velocity += ax * timestep / 2
        self.y_velocity += ay * timestep / 2

        # Append current position to orbit
        self.orbit.append((self.x, self.y))
        if len(self.orbit) > 5000:
            self.orbit.pop(0)

def create_celestial_bodies():
    """
    Initializes celestial bodies with accurate positions and velocities.
    """
    # Sun
    sun = HeavenlyBody("Sun", 1.98847e30, 0, 0, 30, YELLOW)
    sun.is_sun = True

    # Mercury
    mercury = HeavenlyBody("Mercury", 3.30e23, 0.387 * HeavenlyBody.AU, 0, 8, GREY)
    mercury.y_velocity = -47.4e3

    # Venus
    venus = HeavenlyBody("Venus", 4.87e24, 0.723 * HeavenlyBody.AU, 0, 14, WHITE)
    venus.y_velocity = -35.0e3

    # Earth
    earth = HeavenlyBody("Earth", 5.972e24, -HeavenlyBody.AU, 0, 16, BLUE)
    earth.y_velocity = 29.78e3

    # Mars
    mars = HeavenlyBody("Mars", 6.42e23, -1.524 * HeavenlyBody.AU, 0, 12, RED)
    mars.y_velocity = 24.077e3

    # Jupiter
    jupiter = HeavenlyBody("Jupiter", 1.898e27, 5.203 * HeavenlyBody.AU, 0, 20, ORANGE)
    jupiter.y_velocity = -13.07e3

    # Saturn
    saturn = HeavenlyBody("Saturn", 5.683e26, -9.539 * HeavenlyBody.AU, 0, 18, LIGHT_BLUE)
    saturn.y_velocity = 9.69e3

    # Uranus
    uranus = HeavenlyBody("Uranus", 8.681e25, 19.18 * HeavenlyBody.AU, 0, 16, GREY)
    uranus.y_velocity = -6.81e3

    # Neptune
    neptune = HeavenlyBody("Neptune", 1.024e26, -30.06 * HeavenlyBody.AU, 0, 16, PURPLE)
    neptune.y_velocity = 5.43e3

    # Moon (orbiting Earth)
    moon_distance = 3.844e8  # Average distance from Earth to Moon in meters
    moon_orbital_speed = 1.022e3  # Average orbital speed of Moon in m/s
    moon = HeavenlyBody("Moon", 7.34767309e22, earth.x - moon_distance, earth.y, 6, GREY)
    moon.y_velocity = earth.y_velocity + moon_orbital_speed

    return [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, moon]

def main():
    """
    Main function to run the simulation.
    """
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Solar System Simulation")

    bodies = create_celestial_bodies()

    clock = pygame.time.Clock()
    run = True
    show_orbit = True

    # Set up font for labels
    font = pygame.font.SysFont('Arial', 14)

    # Zoom and pan variables
    zoom_level = 0.07  # Adjusted for solar system scale
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
                pygame.quit()
                sys.exit()

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
                    zoom_level = 0.07
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
        timestep = TIMESTEP * simulation_speed
        if simulation_speed != 0:
            for body in bodies:
                body.update_position(bodies, timestep)

        for body in bodies:
            body.draw(screen, zoom_level, offset_x, offset_y, font, show_orbit)

        # Draw labels and info
        info_y_offset = 10
        info_lines = [
            f"Simulation Speed: {simulation_speed}x",
            f"Zoom Level: {zoom_level:.4f}",
            "Controls:",
            "  + / - : Increase/Decrease Simulation Speed",
            "  Mouse Wheel: Zoom In/Out",
            "  Drag Mouse: Pan View",
            "  O: Toggle Orbits",
            "  Space: Pause/Resume Simulation",
            "  R: Reset Simulation",
            "  ESC: Exit Simulation"
        ]

        for line in info_lines:
            label = font.render(line, True, WHITE)
            screen.blit(label, (10, info_y_offset))
            info_y_offset += 18

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
