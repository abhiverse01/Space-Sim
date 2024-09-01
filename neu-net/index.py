import pygame
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
SCALE = 5e-10    # Scale for rendering purposes (meters per pixel)
TIMESTEP = 86400  # One day per simulation step (seconds)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)
GREY = (200, 200, 200)


# Define the neural network model for gravity simulation
class GravityNet(nn.Module):
    def __init__(self):
        super(GravityNet, self).__init__()
        self.fc1 = nn.Linear(6, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 2)  # Output force_x, force_y

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# Function to generate training data
def generate_training_data(num_samples):
    data = []
    for _ in range(num_samples):
        # Random positions and masses
        x1, y1 = np.random.uniform(-1e11, 1e11, 2)
        x2, y2 = np.random.uniform(-1e11, 1e11, 2)
        mass1 = np.random.uniform(1e22, 1e30)
        mass2 = np.random.uniform(1e22, 1e30)

        # Calculate the force using Newton's law
        distance_x = x2 - x1
        distance_y = y2 - y1
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        force = G * mass1 * mass2 / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        # Normalize and create input-output pairs
        input_data = [x1, y1, mass1, x2, y2, mass2]
        input_data_normalized = np.array(input_data) / 1e11  # Normalize positions
        output_data = [force_x, force_y]

        data.append((input_data_normalized, output_data))

    return data

# Function to train the neural network
def train_neural_network(data, epochs=1000):
    model = GravityNet()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)  # Lower learning rate

    for epoch in range(epochs):
        for input_data, output_data in data:
            inputs = torch.tensor(input_data, dtype=torch.float32)
            targets = torch.tensor(output_data, dtype=torch.float32)

            optimizer.zero_grad()
            outputs = model(inputs)

            # Check for NaN in outputs
            if torch.isnan(outputs).any():
                print(f"NaN detected in outputs at epoch {epoch}, skipping this batch.")
                continue

            loss = criterion(outputs, targets)

            # Check for NaN in loss
            if torch.isnan(loss):
                print(f"NaN detected in loss at epoch {epoch}, skipping this batch.")
                continue

            loss.backward()
            optimizer.step()

        if epoch % 100 == 0:
            print(f'Epoch {epoch}, Loss: {loss.item()}')

    return model

# Initialize and train the neural network
training_data = generate_training_data(100)
model = train_neural_network(training_data)

# Modify the HeavenlyBody class to use the neural network for force calculation
class HeavenlyBody:
    def __init__(self, name, mass, x, y, radius, color):
        self.name = name
        self.mass = mass
        self.x = x  # Position in meters
        self.y = y
        self.radius = radius  # Radius in pixels
        self.color = color
        self.x_velocity = 0  # Velocity in m/s
        self.y_velocity = 0
        self.orbit = []

    def draw(self, screen, zoom, pan_x, pan_y, show_orbit=True):
        x = (self.x * SCALE * zoom + screen.get_width() // 2) + pan_x
        y = (self.y * SCALE * zoom + screen.get_height() // 2) + pan_y

        pygame.draw.circle(screen, self.color, (int(x), int(y)), int(self.radius * zoom))

        if show_orbit and len(self.orbit) > 2:
            orbit_scaled = [(pos[0] * zoom + pan_x, pos[1] * zoom + pan_y) for pos in self.orbit]
            pygame.draw.aalines(screen, self.color, False, orbit_scaled, 1)

    def attraction(self, other_body):
        # Use the neural network to predict the force
        input_data = np.array([self.x, self.y, self.mass, other_body.x, other_body.y, other_body.mass]) / 1e11
        input_tensor = torch.tensor(input_data, dtype=torch.float32)
        force_x, force_y = model(input_tensor).detach().numpy()

        # Check for NaN and replace with zero if found
        if math.isnan(force_x) or math.isnan(force_y):
            force_x, force_y = 0.0, 0.0

        return force_x, force_y


    def update_position(self, bodies, screen, zoom, pan_x, pan_y):
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue
            fx, fy = self.attraction(body)
            total_fx += fx
            total_fy += fy

        # Update velocities based on acceleration
        self.x_velocity += (total_fx / self.mass) * TIMESTEP
        self.y_velocity += (total_fy / self.mass) * TIMESTEP

        # Update positions based on velocity
        self.x += self.x_velocity * TIMESTEP
        self.y += self.y_velocity * TIMESTEP

        # Append current position to orbit
        orbit_x = (self.x * SCALE * zoom + screen.get_width() // 2) + pan_x
        orbit_y = (self.y * SCALE * zoom + screen.get_height() // 2) + pan_y
        self.orbit.append((orbit_x, orbit_y))
        if len(self.orbit) > 500:
            self.orbit.pop(0)

# Define the main function
def main():
    pygame.init()
    width, height = 800, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Heavenly Bodies Simulation")
    
    # Define celestial bodies with adjusted sizes
    sun = HeavenlyBody("Sun", 1.989e30, 0, 0, 15, YELLOW)
    
    earth_distance = 1.496e11  # Distance from Sun to Earth in meters
    earth = HeavenlyBody("Earth", 5.972e24, earth_distance, 0, 8, BLUE)
    earth.y_velocity = -29.78e3  # Earth's orbital velocity in m/s
    
    moon_distance = 3.844e8  # Distance from Earth to Moon in meters
    moon = HeavenlyBody("Moon", 7.34767309e22, earth_distance + moon_distance, 0, 3, GREY)
    moon.y_velocity = earth.y_velocity - 1.022e3  # Moon's orbital velocity relative to Earth
    
    bodies = [sun, earth, moon]
    
    clock = pygame.time.Clock()
    run = True
    show_orbit = True
    zoom = 1.0
    pan_x, pan_y = 0, 0

    # Set up font for labels
    font = pygame.font.SysFont('Arial', 16)
    
    while run:
        clock.tick(60)  # Limit to 60 FPS
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    show_orbit = not show_orbit
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom += 0.1
                if event.key == pygame.K_MINUS:
                    zoom -= 0.1
                if event.key == pygame.K_LEFT:
                    pan_x += 20
                if event.key == pygame.K_RIGHT:
                    pan_x -= 20
                if event.key == pygame.K_UP:
                    pan_y += 20
                if event.key == pygame.K_DOWN:
                    pan_y -= 20
        
        for body in bodies:
            body.update_position(bodies, screen, zoom, pan_x, pan_y)
            body.draw(screen, zoom, pan_x, pan_y, show_orbit)

        # Draw labels at the top-right corner
        label_y_offset = 10
        for body in bodies:
            label = font.render(f"{body.name}: x={int(body.x/1e9)}Gm, y={int(body.y/1e9)}Gm", True, WHITE)
            screen.blit(label, (10, label_y_offset))
            label_y_offset += 20
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
