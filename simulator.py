import tkinter as tk
from tkinter import simpledialog
from vpython import canvas, cylinder, arrow, vector, color, rate
import numpy as np
import streamlit as st

# Convert wavelength (nm) to approximate RGB color
def wavelength_to_rgb(wavelength):
    gamma = 0.8
    intensity_max = 1.0
    if 380 <= wavelength <= 440:
        R, G, B = -(wavelength - 440) / 60, 0.0, 1.0
    elif 440 < wavelength <= 490:
        R, G, B = 0.0, (wavelength - 440) / 50, 1.0
    elif 490 < wavelength <= 510:
        R, G, B = 0.0, 1.0, -(wavelength - 510) / 20
    elif 510 < wavelength <= 580:
        R, G, B = (wavelength - 510) / 70, 1.0, 0.0
    elif 580 < wavelength <= 645:
        R, G, B = 1.0, -(wavelength - 645) / 65, 0.0
    elif 645 < wavelength <= 780:
        R, G, B = 1.0, 0.0, 0.0
    else:
        R = G = B = 0.0
    if 380 <= wavelength <= 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / 40
    elif 420 < wavelength <= 700:
        factor = 1.0
    elif 700 < wavelength <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength) / 80
    else:
        factor = 0.0
    def adjust(c):
        return 0.0 if c == 0 else (intensity_max * (c * factor)) ** gamma
    return vector(adjust(R), adjust(G), adjust(B))

# Optical rotation calculation (radians)
def optical_rotation_angle(conc, wavelength, length=1.0):
    spec_deg = 66.0 * (589.0 / wavelength) ** 2
    angle_deg = spec_deg * conc * (length * 10)
    return np.deg2rad(angle_deg)

# Main simulation function
def main():
    # GUI input
    root = tk.Tk(); root.withdraw()
    conc = simpledialog.askfloat("Sucrose Concentration", "Enter concentration (g/mL):", minvalue=0.0)
    wav = simpledialog.askfloat("Laser Wavelength", "Enter wavelength (nm, 380-780):", minvalue=380, maxvalue=780)
    if conc is None or wav is None:
        return

    # Compute parameters
    length = 1.0       # container length (m)
    radius = 0.15      # cylinder radius (m)
    beam_radius = 0.003  # thinner beam for visibility
    n_slices = 500    # segments for smooth gradient
    angle = optical_rotation_angle(conc, wav, length)
    rgb = wavelength_to_rgb(wav)

    # Expected number of intensity cycles (two dark/light per pi)
    cycles = angle / np.pi

    # Setup scene
    scene = canvas(title="Smooth Optical Rotation Fringes",
                   width=800, height=600, center=vector(0,0,0.5))
    # Axes
    arrow(pos=vector(0,0,0), axis=vector(1,0,0), shaftwidth=0.002, color=color.red)
    arrow(pos=vector(0,0,0), axis=vector(0,1,0), shaftwidth=0.002, color=color.green)
    arrow(pos=vector(0,0,0), axis=vector(0,0,1), shaftwidth=0.001, color=vector(0,0,0))

    # Draw container with moderate opacity
    cylinder(pos=vector(0,0,0), axis=vector(0,0,length), radius=radius, opacity=0.4)

    # Draw beam as segmented cylinders with smooth opacity gradient
    dz = length / n_slices
    for i in range(n_slices):
        z0 = i * dz
        theta = (z0 / length) * angle
        intensity = np.cos(theta) ** 2
        # Draw each segment
        cylinder(pos=vector(0,0,z0), axis=vector(0,0,dz), radius=beam_radius,
                 color=rgb, opacity=intensity)
        rate(200)

    # Caption with expected cycles
    scene.caption = (f"Conc: {conc} g/mL, λ: {wav} nm, Total Rot: {np.rad2deg(angle):.1f}°, "
                     f"Expected Cycles: {cycles:.2f}")

    scene.waitfor('click')

if __name__ == '__main__':
    main()
