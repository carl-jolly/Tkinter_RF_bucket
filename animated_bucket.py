import tkinter as tk
import numpy as np
import random

# Constants
WIDTH, HEIGHT = 600, 600
PARTICLE_RADIUS = 2  # Very small width and height to simulate a point
NUM_PARTICLES = 1000

h = 4
gamma_t = 5.034
E0 = 938.272e6
init_phi_s = 0

scale_factor = 20 # scale factor to artificially boost the bucket size so it can be seen on the plot
init_V1 = 19e3*scale_factor # volts

C0 = 10*16.3363 # ISIS circumference
q = 1

class Particle:
    def __init__(self, canvas, color, KE, phi_s, RF_volts):
        self.canvas = canvas
        self.color = color

        self.phi_n = random.uniform(-np.pi*0.75, np.pi*0.75) 
        #self.phi_n = random.uniform(0.0, 0.0) 
        #self.E =  random.uniform(-0.01e6, -0.01e6) 
        self.E =  random.uniform(-2e6, 2e6) 

        self.KE = KE
        
        self.phi_s = phi_s
        self.RF_volts = RF_volts

        self.shape = canvas.create_oval(self.phi_n - PARTICLE_RADIUS, self.E/5e4 - PARTICLE_RADIUS,
                                        self.phi_n + PARTICLE_RADIUS, self.E/5e4 + PARTICLE_RADIUS,
                                        fill=color)

    def update(self):
        gamma = (self.E + self.KE)/E0 + 1 
        beta = np.sqrt(1 - (1/(gamma*gamma)))
        phase_slip = 1/(gamma*gamma) - 1/(gamma_t*gamma_t)

        # These equations update the energy and phase of the particle as it moves in the longitudinal phase space.

        # h= 2
        if h == 2:
            self.E =  self.E + self.RF_volts * (np.sin(self.phi_n) - np.sin(self.phi_s))
            
            self.KE += self.RF_volts * np.sin(self.phi_s) 

        # h = 4
        if h == 4:
            theta = np.pi
            self.E =  self.E + self.RF_volts * (np.sin(self.phi_n) - np.sin(self.phi_s)) + self.RF_volts * (np.sin(2*self.phi_n+theta) - np.sin(2*self.phi_s+ theta))
            
            self.KE += self.RF_volts * (np.sin(self.phi_s) + np.sin(2*self.phi_s + 0)) 

        self.phi_n =   self.phi_n -  ( (2*np.pi * h * phase_slip)/(E0 * beta*beta * gamma) ) * self.E

        # KE printout 
        KE_label.config(text=f"Kinetic Energy [MeV]: {self.KE*1e-6:.2f}")

        #print("KE MeV] = ", self.KE/1e6)
        if self.phi_n > 2*np.pi: # particles that go off the plot come back from the other side, ie no particles can be lost
            self.phi_n = -2*np.pi
        if self.phi_n < -2*np.pi:
            self.phi_n = 2*np.pi

        self.canvas.coords(self.shape, (WIDTH/2 + self.phi_n*5e1 - PARTICLE_RADIUS),
                           (HEIGHT/2 + self.E/5e4 - PARTICLE_RADIUS),
                          ( WIDTH/2 + self.phi_n*5e1 + PARTICLE_RADIUS),
                           (HEIGHT/2 + self.E/5e4 + PARTICLE_RADIUS))
        
def update_phis(value):
    new_phi_s = float(value) 
    for particle in particles:
        particle.phi_s = new_phi_s*np.pi/180

def update_rf_volts(value):
    new_RF_volts = float(value)*1e3*scale_factor 
    for particle in particles:
        particle.RF_volts = new_RF_volts

def animate():
    for particle in particles:
        particle.update()
    root.after(20, animate)

root = tk.Tk()
root.title("Longitudinal phase space")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
canvas.pack()

canvas.create_line(0, HEIGHT/2, WIDTH, HEIGHT/2, fill='black')  # x-axis
canvas.create_line(WIDTH/2, 0, WIDTH/2, HEIGHT, fill='black')  # y-axis

KE_label = tk.Label(root, text="Kinetic Energy [MeV]: 0.00")
KE_label.pack()


# Create a slider to change phis
phis_var = tk.DoubleVar()
phis_var.set(init_phi_s)
phis_slider = tk.Scale(root, from_=0.0, to=45, orient="horizontal", resolution=0.1, label="phi_s [deg]", variable=phis_var, command=update_phis)
phis_slider.pack()

# Create a slider to change RF volts
volts_var = tk.DoubleVar()
volts_var.set(init_V1/1e3/scale_factor)
volts_slider = tk.Scale(root, from_=0.0, to=200, orient="horizontal", resolution=0.1, label="RF voltage [kV]", variable=volts_var, command=update_rf_volts)
volts_slider.pack()

# Create a list of particles
particles = [Particle(canvas, 'blue', KE=70.44e6, phi_s=init_phi_s, RF_volts=init_V1) for _ in range(NUM_PARTICLES)]

animate()

# Run the tkinter main loop
root.mainloop()
