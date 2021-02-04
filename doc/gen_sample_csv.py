#!/usr/bin/env python3

from math import pi, sin, cos, tan


def generate_angle_data(start, end, incr):
    curr_angle = start
    angle_data = []

    while curr_angle < end:
        angle_data.append((curr_angle, sin(curr_angle),
                           cos(curr_angle), tan(curr_angle)))
        curr_angle += incr

    return angle_data


def write_angles_to_file(filename, angle_data):
    with open(filename, 'w') as f:
        f.write('angle, sin, cos, tan\n')
        for row in angle_data:
            f.write(', '.join([str(value) for value in row]) + '\n')


if __name__ == '__main__':
    angle_data = generate_angle_data(0, 4*pi, 2*pi/100)
    write_angles_to_file('angle_data.csv', angle_data)
