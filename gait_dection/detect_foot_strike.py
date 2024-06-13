import heapq
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from vicon import Vicon

right_foot_markers = (
    'RD2P',
    'RD5P',
    'RHEE',
    'RLATH',
    'RD5M',
    'RD1M',
    'RP1M',
)

left_foot_markers = (
    'LD2P',
    'LD5P',
    'LHEE',
    'LLATH',
    'LD5M',
    'LD1M',
    'LP1M',
)

class Marker:
    def __init__(self, name: str, vicon: Vicon):
        self.marker = name
        self.markers = left_foot_markers + right_foot_markers
        self.z_coords = {marker: [] for marker in self.markers}
        self.y_coords = {marker: [] for marker in self.markers}
        self.x_coords = {marker: [] for marker in self.markers}
        self.z_velo = {marker: [] for marker in self.markers}
        self.z_accel = {marker: [] for marker in self.markers}

        for marker in self.markers:
            trajectory = vicon.fetch_trajectory(marker)
            for i in range(len(trajectory)):
                print(trajectory[i])
                self.z_coords[marker].extend(trajectory[i][2])
                self.y_coords[marker].extend(trajectory[i][1])
                self.x_coords[marker].extend(trajectory[i][0])
                self.z_velo[marker].extend(np.gradient(self.z_coords[marker])) 
                self.z_accel[marker].extend(np.diff(self.z_coords[marker], 2))

    def find_foot_strike(self, lower_frame_bound: int = 0) -> list:
        foot_down_frames = []
        def is_z_accel_peak(i, threshold: float = 4):
            return marker_z_accel[i] > threshold and marker_z_accel[i-1] < marker_z_accel[i] > marker_z_accel[i+1]
    
        def is_z_velo_trough(i, threshold: float = -4):
            return marker_z_velo[i] < threshold and marker_z_velo[i-1] > marker_z_velo[i] < marker_z_velo[i+1]
        
        z_accel_peak = z_velo_trough = False
        marker_z_accel = self.z_accel[self.marker]
        marker_z_velo = self.z_velo[self.marker]
        marker_z_pos = self.z_coords[self.marker]
    
        for i in range(1, len(marker_z_accel) - 1):
            if is_z_accel_peak(i):
                z_accel_peak = True    

            if is_z_velo_trough(i):
                z_velo_trough = True

            if z_accel_peak and z_velo_trough and marker_z_accel[i-1] > marker_z_velo[i-1] and marker_z_accel[i] < marker_z_velo[i] and marker_z_pos[i] < 120:
                foot_down_frames.append(i + lower_frame_bound)
                z_accel_peak = z_velo_trough = False

        return foot_down_frames

    def find_frames_from_data(self, list1: list, list2: list, list3: list) -> list:
        points = []
        heap = []
        final_points = []
        if list1:
            heapq.heappush(heap, (list1[0], 0, list1))
        if list2:
            heapq.heappush(heap, (list2[0], 0, list2))
        if list3:
            heapq.heappush(heap, (list3[0], 0, list3))

        while heap:
            value, idx, arr = heapq.heappop(heap)
            points.append(value)
            if idx + 1 < len(arr):
                heapq.heappush(heap, (arr[idx + 1], idx + 1, arr))

        diff = 0
        in_bounds = False
        for i in range(len(points)-1):
            diff = abs(points[i] - points[i+1])
            if diff <= 19 and not in_bounds:
                final_points.append(points[i])
                in_bounds = True
            elif diff > 19:
                in_bounds = False

        return final_points

    def plot_markers(self, lower_bound: int, upper_bound: int):
        plt.figure(figsize=(10,6))

        for marker in self.markers:
            frames = np.arange(lower_bound, upper_bound)
            plt.plot(frames, self.z_coords[marker], label = marker + ' z coord')
            plt.plot(frames, self.z_velo[marker], label = marker + ' z velo')
            frames = np.arange(lower_bound, upper_bound - 2)
            plt.plot(frames, self.z_accel[marker], label = marker + ' z accel')

        plt.xlabel('Frame')
        plt.title('Kinematics over time')
        plt.legend()
        plt.grid(True)
        plt.show()

def main():
    vicon = Vicon()
    lower, upper = vicon.get_region_of_interest()
    marker = Marker('RD2P', vicon)
    marker.plot_markers(lower, upper)
    for marker in right_foot_markers:
        lis = marker.find_foot_strike(lower)
        print(lis)
    # print(marker.find_frames_from_data(list1, list2, list3))

if __name__ == "__main__":
    main()