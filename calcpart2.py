"""
file: calcpart2.py
description: Predicts the velocity of the Tesla Model S P100D more accurately
language: python3
author: Evan Prizel (emp4506)
"""

import math
import matplotlib.pyplot as plt
from math import pi
from HelperFunctions import *

# p100d constants
gravity = 9.81  # (g) m/s^2
air_density = 1.2041  # (p) kg/m^3
mass = 2250  # (m) kg
drag_coefficient = 0.24  # (C (sub) D)
tire_radius = 14.15  # (r) in
static_friction = 1.11  # (u (sub) s)
surface_area = 2.1  # (A) m^2
gear_reduction = 9.325  # (G)
max_motor_torque = 980  # (T (sub) max) Nm
max_motor_power = 450.4  # (P (sub) max) kW
max_motor_torque_regime = 4000  # (R (sub) 1) rpm
max_motor_power_regime = 5750  # (R (sub) 2) rpm
max_velocity = 150  # (v (sub) max) mph
max_motor_rpm = 16614  # (R (sub) max) rpm
time_step = 0.01  # (delta t) s

# graph constants
x_min = 1.3
x_max = 2
y_min = 6
y_max = 12

# zeperfs values
zeperfs_x = [0, 0.26, 1.46, 2.26, 3.16, 4.06, 4.56, 7.46, 9.26, 11.66, 18.66]
zeperfs_y = [0, 5.9, 31.1, 49.7, 62.1, 74.6, 80.8, 99.4, 111.8, 124.3, 149.1]


# Euler's method
# v0 = 0
# v1 = v0 + H(v0)time_step
# vn+1 = vn + H(vn)time_step

def make_plot():
    """
    This makes the plot with bounds, labels and steps for each axis.
    """
    plt.title('Tunable Factor vs RSME')
    plt.xlabel('Tunable Factor')
    plt.ylabel('RSME')
    plt.axis([x_min, x_max, y_min, y_max])
    plt.xticks([x / 10 for x in range(13, 21)])
    plt.yticks(range(y_min, y_max + 1, 1))


def calculate_imparted_force(rpm, t):
    """
    Calculates the force imparted on the road by the tires. (equation 5)
    :param rpm: The RPM of the motor.
    :param t: The tunable factor.
    :return: Imparted force in Newtons.
    """
    if rpm <= max_motor_torque_regime:
        return (gear_reduction * max_motor_torque) / in_to_m(
            tire_radius)

    if max_motor_torque_regime < rpm < max_motor_power_regime:
        part_1 = (((9549.3*max_motor_power)/max_motor_power_regime)-max_motor_torque) / (max_motor_power_regime - max_motor_torque_regime)
        part_2 = (rpm - max_motor_torque_regime)

        return (gear_reduction * tunable_factor(rpm, t) * ((part_1 * part_2) + max_motor_torque)) / in_to_m(tire_radius)

    if max_motor_power_regime <= rpm:
        return (gear_reduction * tunable_factor(rpm, t) * ((9549.3 * max_motor_power) / rpm)) / in_to_m(tire_radius)


def tunable_factor(rpm, t):
    """
    This calculates the torque factor for the motor.
    :param rpm: The rpm of the motor.
    :param t: the tunable factor
    :return: the torque.
    """
    return 1 - ((rpm - max_motor_torque_regime) / (t * max_motor_rpm))


def calculate_rpm(velocity):
    """
    Calculates the RPM of the motor. (Equation 4)
    :param velocity: The velocity of the car.
    :return: The rpm of the motor at the velocity the car is traveling at.
    """
    return (60 * gear_reduction * velocity) / (2 * pi * in_to_m(tire_radius))


def calculate_force(velocity, t):
    """
    This calculates the force pushing the car forward limited by max static
    friction.
    :param velocity: The velocity of the car
    :param t: The tunable factor.
    :return: The calculated force.
    """
    return min((static_friction * mass * gravity),
               calculate_imparted_force(calculate_rpm(velocity), t))


def calculate_aerodynamic_drag(velocity):
    """
    Calculates the aerodynamic drag of the car. (second part of inside the
    parenthesis of equation 3)
    :param velocity: The velocity of the car/
    :return: The aerodynamic drag of the car.
    """
    return 0.5 * (air_density * drag_coefficient * surface_area * (velocity ** 2))


def calculate_acceleration(velocity, t):
    """
    Calculates the acceleration of the car. (Equation 3)
    :param velocity: The velocity of the car.
    :param t: The tunable factor.
    :return: The acceleration of the car.
    """
    return (calculate_force(velocity, t) - calculate_aerodynamic_drag(velocity)) / mass


def calculate_velocity(t):
    """
    This calculates the velocity of the car using Euler's method.
    :param t: The tunable factor.
    :return: A dictionary with the velocity at each time_step
    """
    x, y = [0], [0]
    current_time = 0.01
    Vn = 0
    for throwaway in range(int(20 / time_step)):
        velocity = Vn + (calculate_acceleration(Vn, t) * time_step)
        x.append(current_time)
        y.append(mps_to_mph(velocity))
        current_time += time_step
        Vn = velocity
    return x, y


def compare_values(y):
    """
    This compares my values to the values from zeperfs.
    :param y: The velocities list I created.
    """
    plt.scatter(zeperfs_x, zeperfs_y)

    for i in range(len(zeperfs_x)):
        if i == 0:
            print(str(zeperfs_x[i]) + '\t\t' + str(
                y[int(zeperfs_x[i] * 100)]) + '\t\t\t\t\t' + str(zeperfs_y[i]))
        else:
            print(str(zeperfs_x[i]) + '\t' + str(
                y[int(zeperfs_x[i] * 100)]) + '\t' + str(zeperfs_y[i]))


def calculate_rsme(y):
    """
    This calculates the RSME.
    :param y: The velocities list I created.
    :return: The rsme value.
    """
    total_value = 0
    for i in range(len(zeperfs_x)):
        total_value += ((zeperfs_y[i] - y[int(zeperfs_x[i] * 100)]) ** 2)
    return math.sqrt(total_value)


def main():
    """
    This will make the graph and run the program to find the optimal tunable
    force, and then use said optimal tunable force to calculate the velocity of
    the p100d.
    """
    make_plot()
    tunable = []
    rsme_list = []
    t = 1.3
    while t < 2.01:
        x, y = calculate_velocity(t)
        rsme = calculate_rsme(y)
        tunable.append(t)
        rsme_list.append(rsme)
        t += 0.01
    optimal_tunable_factor = tunable[rsme_list.index(min(rsme_list))]
    print("This is the optimal tunable factor:", optimal_tunable_factor)
    plt.plot(tunable, rsme_list)
    plt.show()
    plt.title('Tesla Model S P100D Time vs Velocity')
    plt.xlabel('Time (sec)')
    plt.ylabel('Velocity (mph)')
    plt.axis([x_min, x_max, y_min, y_max])
    plt.xticks(range(0, 20 + 1, 2))
    plt.yticks(range(0, 200 + 1, 20))
    x, y = calculate_velocity(optimal_tunable_factor)
    plt.plot(x, y)
    plt.scatter(zeperfs_x, zeperfs_y)
    plt.show()


if __name__ == '__main__':
    main()
