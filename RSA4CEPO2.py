#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/3 9:24
# @Author  : Xavier Ma
# @Email   : xavier_mayiming@163.com.com
# @File    : RSA4CEPO.py
# @Statement : The ripple-spreading algorithm for the co-evolutionary path optimization
# @Reference : HU X B,ZHANG M K,ZHANG Q,et al.Co-evolutionary path optimization by ripple-spreading algorithm[J].Transportation Research:Part B,2017,106:411-432.
import os
import math
import copy
import helpfunction
import matplotlib.pyplot as plt
import Initial_network
import time
import datetime
import Draw_path
import geo


def find_neighbor(network):
    """
    Find the neighbor of each node
    :param network: {node1: {node2: length, node3: length, ...}, ...}
    :return: {node 1: [the neighbor nodes of node 1], ...}
    """
    nn = len(network)
    neighbor = []
    for i in range(nn):
        neighbor.append(list(network[i].keys()))
    return neighbor


def find_speed(network, neighbor):
    """
    Find the ripple spreading speed
    :param network: {node1: {node2: length, node3: length, ...}, ...}
    :param neighbor: the neighbor set
    :return:
    """
    speed = 1e10
    for i in range(len(network)):
        for j in neighbor[i]:
            speed = min(speed, network[i][j])
    return speed


def routing_environmental_dynamics(network, t, v, flighnum, start_time, node_lock_periods):
    """
    The obstacle moves from the lower right corner to the upper left corner
    :param network: {node1: {node2: length, node3: length, ...}, ...}
    :param t: current time index
    :param orad: the radius of the obstacle
    :param ospeed: the moving speed of the obstacle
    :param x: the x axis coordinates of nodes
    :param y: the y axis coordinates of nodes
    :return:
    """

    # 当前第i架飞机所处的时间信息来计算当前别的飞机的位置信息
    # init_time = datetime.datetime(2023, 4, 17, 7, 0)
    active_node = [i for i in range(len(network))]
    inactive_node = []

    t1 = t * v
    current_time = start_time + t1

    # Check each node to see if it should be inactive at the current time
    for node, lock_periods in node_lock_periods.items():
        for start_time, end_time in lock_periods:
            # print('endtime',end_time,current_time)
            if start_time <= current_time < end_time:
                inactive_node.append(node)
                if node in active_node:
                    active_node.remove(node)
                break  # No need to check other lock periods for this node

    # Copy the network and remove inactive nodes
    new_network = copy.deepcopy(network)
    for i in inactive_node:
        new_network[i] = {}
        for j in new_network:
            new_network[j].pop(i, None)  # Remove inactive nodes from the adjacency list of other nodes

    return new_network, active_node, inactive_node




def main(network, in_angles, out_angles, source, destination, flighnum, pointcoordlist, theairport,
         network_point, start_time, node_lock_periods, points):
    """
    The main function of the RSA4CEPO
    :param network: {node1: {node2: length, node3: length, ...}, ...}
    :param source: the source node
    :param destination: the destination node
    :param x: the x axis coordinates of nodes
    :param y: the y axis coordinates of nodes
    :param orad: the radius of the obstacle
    :param ospeed: the moving speed of the obstacle
    """

    # Step 1. Initialization
    nn = len(network)  # node number
    neighbor = find_neighbor(network)  # the neighbor set
    v = find_speed(network, neighbor)  # the ripple spreading speed
    # print("speed", v)
    t = 0  # simulated time index
    nr = 0  # the current number of ripples - 1
    epicenter_set = []  # epicenter set
    radius_set = []  # radius set
    length_set = []  # length set
    path_set = []  # path set
    state_set = []
    activation_times = {}
    # state set, state_set[i] = 1, 2, 3 means ripple i is waiting, active, or dead
    omega = {}  # the set that records the ripple generated at each node
    pushback_points = helpfunction.find_pushback_points(points, pointcoordlist)

    for node in range(nn):
        omega[node] = -1

    # Step 2. Initialize the first ripple
    epicenter_set.append(source)
    radius_set.append(0)
    length_set.append(0)
    path_set.append([source])
    state_set.append(2)
    activation_times[source] = int(t*v)
    omega[source] = nr
    nr += 1
    k = 0

    # Step 3. The main loop
    # print("des", destination)

    while omega[destination] == -1:
        # print(path_set)
        # print(omega[destination], "Iteration:", k)
        k += 1
        # Step 3.1. If there is no feasible solution
        flag = True
        for state in state_set:
            # print(state_set)
            if state == 1 or state == 2:
                flag = False
                break
        if flag:
            print('There is no feasible solution!')
            return {}

        # Step 3.2. Time updates
        t += 1
        incoming_ripples = {}

        # Step 3.3. Update the obstacle based on the given routing environmental dynamics
        # if flighnum == 0:
        new_network, active_node, inactive_node = routing_environmental_dynamics(network, t, v, flighnum,
                                                                                 start_time, node_lock_periods)
        # if inactive_node:
            # print(inactive_node)
        # new_neighbor = find_neighbor(new_network)

        for i in range(nr):  # waiting nodes -> active nodes
            if state_set[i] == 1 and epicenter_set[i] in active_node:
                state_set[i] = 2
            # if state_set[i] == 1 and path_set[i][-2] in inactive_node:
            #     print('inactive_node activated')
            #     state_set[i] = 3

        for i in range(nr):
            # print("i", i)
            if state_set[i] == 2:
                # Step 3.4. Active ripple spreads out
                radius_set[i] += v
                epicenter = epicenter_set[i]
                radius = radius_set[i]
                path = path_set[i]
                length = length_set[i]

                # Step 3.5. New incoming ripples
                # for node in new_neighbor[epicenter]:
                for node in neighbor[epicenter]:
                    # print("neigh", neighbor[epicenter])
                    if omega[node] == -1 or (node in pushback_points):  # the node has not been visited yet
                        temp_length = network[epicenter][node]
                        in_angle = in_angles[epicenter][node]
                        if temp_length <= radius < temp_length + v:
                            # Step 3.6. Accessible node
                            if len(path) > 1:
                                ang_rad = out_angles[path[-2]][epicenter] - in_angle
                                delta = math.cos(ang_rad)  # if len(path) > 1 else 1
                                if (ang_rad / 3.141592653589793) == 1.5:
                                    delta = 0  # 控制有1.5pi 等于0 实际为负数
                            else: delta = 1
                            # print(path)
                            # pathcood = helpfunction.list2node(path, pointcoordlist)
                            # print('path :', helpfunction.print_plist(pathcood, points))

                            if 0 <= delta and node in active_node:
                                temp_path = path.copy()
                                temp_path.append(node)
                                if node in incoming_ripples.keys():
                                    incoming_ripples[node].append({
                                        'path': temp_path,
                                        'radius': radius - temp_length,
                                        'length': length + temp_length,
                                        'state': 2
                                    })
                                else:
                                    incoming_ripples[node] = [{
                                        'path': temp_path,
                                        'radius': radius - temp_length,
                                        'length': length + temp_length,
                                        'state': 2
                                    }]

                            # Step 3.7. Inaccessible node
                            if 0 <= delta and node in inactive_node:
                                temp_path = path.copy()
                                temp_path.append(node)
                                if node in incoming_ripples.keys():
                                    incoming_ripples[node].append({
                                        'path': temp_path,
                                        'radius': 0,
                                        'length': length + temp_length,
                                        'state': 1
                                    })
                                else:
                                    incoming_ripples[node] = [{
                                        'path': temp_path,
                                        'radius': 0,
                                        'length': length + temp_length,
                                        'state': 1
                                    }]

        # Step 3.8. Generate new ripples
        for node in incoming_ripples.keys():
            if node in active_node:
                new_ripple = sorted(incoming_ripples[node], key=lambda x: x['radius'], reverse=True)[
                    0]  # the ripple with the largest radius is selected
            else:
                new_ripple = sorted(incoming_ripples[node], key=lambda x: x['length'])[
                    0]  # the ripple with the smallest length is selected
            epicenter_set.append(node)
            radius_set.append(new_ripple['radius'])
            length_set.append(new_ripple['length'])
            path_set.append(new_ripple['path'])
            state_set.append(new_ripple['state'])
            activation_times[node] = int(t*v)
            omega[node] = nr
            nr += 1

        # Step 3.9. Determine whether the ripple turns to be dead
        for i in range(nr):
            if state_set[i] == 1 or state_set[i] == 2:
                flag = True
                epicenter = epicenter_set[i]
                # print("epocenter", epicenter)
                # print("nextnode", network_point[pointcoordlist[epicenter]])
                # print("{} neighbor".format(epicenter), neighbor[epicenter])
                for node in neighbor[epicenter]:
                    if omega[node] == -1 or node in pushback_points:
                        flag = False
                        break
                if flag:
                    state_set[i] = 3

    # Step 4. Plot the path
    ripple = omega[destination]

    # 将数字形式的链表，转换成point的坐标形式
    plist = helpfunction.list2node(path_set[ripple], pointcoordlist)

    # Convert the path to list of activation times
    path_activation_times = [activation_times[node] for node in path_set[ripple]]  # <<< New code here

    # Draw_path.create_bokeh_animation(network_point, network, pointcoordlist, t, v, path, plist)
    # Draw_path.create_bokeh_animation_with_path(network_point, network, pointcoordlist, t, v, path_set[ripple], plist)
    # 按顺序打印最终路径的节点信息
    # helpfunction.print_plist(plist, points = theairport.points)
    # findpath.interactive_plot_network(network_point, x, y, pointcoordlist, plist)

    return path_set[ripple], length_set[ripple], plist, t, v, path_activation_times

