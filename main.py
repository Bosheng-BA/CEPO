import sys
import os.path
import tkinter
import airport
import traffic
import hmi
import hmi2
import Initial_network
import RSA4CEPO2
import time
import datetime
import helpfunction
import Draw_path
import Sour_and_Des
import gaptraffic
import json
import os
import Cst
from tqdm import tqdm
# above imported library
""" Default airport and traffic files """
DATA_PATH = "Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
# FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_STD.B&B.sim")
FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_16R.B&B.sim")


# 函数，将列表写入到json文件
def write_list_to_json(list_name, filename):
    with open(filename, 'w') as f:
        json.dump(list_name, f)


# 函数，将列表写入到文件
def write_list_to_file(list_name, filename):
    with open(filename, 'w') as f:
        for item in list_name:
            f.write("%s\n" % item)


def get_node_lock_periods(pathlist, activation_times_list, network_cepo, flight, node_lock_periods):
    # node_lock_periods = {}

    # for path_index in range(len(pathlist)):
    path = pathlist[-1]
    activation_times = activation_times_list[-1]
    if flight.departure == 'ZBTJ':
        startt = flight.ttot - 600
    else:
        startt = flight.aldt
    flight_start_time = startt
    # flight_start_time = 0

    for i in range(1, len(path) - 1):  # Start from the second node in the path
        node = path[i]
        prev_node = path[i - 1]
        next_node = path[i + 1]

        # The node should be locked as soon as the previous node is reached
        start_time = activation_times[i-1] + flight_start_time
        end_time = start_time + network_cepo[prev_node][node]

        # Determine the end of the lock period based on the distance to the next node
        distance_to_next_node = network_cepo[node][next_node]
        if distance_to_next_node > 20:
            end_time += 20
        else:
            end_time += distance_to_next_node

        # Add the lock period to the node's list of lock periods
        if node not in node_lock_periods:
            node_lock_periods[node] = []
        node_lock_periods[node].append((start_time, end_time))

    return node_lock_periods


def find_routing(the_airport, the_airport2, sour, des, flight, flightnum, network, pointcoordlist, network_cepo,
             in_angles, out_angles, in_angles_cepo, out_angles_cepo, node_lock_periods, start_time):

    s = pointcoordlist.index(sour)
    d = pointcoordlist.index(des)

    """CEPO 寻路过程"""
    path_set, length_set, plist, t, v, path_activation_times = \
        RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d, flightnum, pointcoordlist,
                       the_airport2, network, start_time, node_lock_periods, the_airport2.points)

    # Draw_path.create_matplotlib_figure(network_point=network, pointcoordlist=pointcoordlist, path=plist, stand=s,
    #                                    runway=d, flightnum=flightnum)
    # print(path_activation_times[-1])
    cost = path_activation_times[-1]

    return path_set, plist, path_activation_times, cost


if __name__ == "__main__":
    fpl_file = sys.argv[1] if 1 < len(sys.argv) else FPL_FILE
    # Load the airport and the traffic
    the_airport = airport.load(APT_FILE)
    the_airport2 = airport.load2(APT_FILE)

    filename = Cst.flight_file_name
    flights = gaptraffic.read_flights(filename)
    node_lock_periods = {}
    activation_times_list = []
    pathlist = []  # 按照飞机的顺序储存飞机的节点序号路径
    path_coordlist = []  # 按照飞机的顺序储存飞机的节点坐标路径

    stand_dict, runway_dict, stand_list, stand_dict2, runway_list, runway_dict2 \
        = Sour_and_Des.stand_and_runway_points(points=the_airport2.points)
    network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo, init_l \
        = Initial_network.initial_network(the_airport2)

    costs = []
    Total_COST = 0
    init_Tcost = 0
    turn_times = 0
    Tcost_without_waiting = 0
    Lenth = 0
    for flightnum in tqdm(range(len(flights)), ncols= 100):
    # for flightnum in range(0, 1):
        flight = flights[flightnum]
        # 多飞机规划路径：
        # 初始化开始时间
        init_time = datetime.datetime(2023, 4, 17, 7, 0)

        if flight.departure == 'ZBTJ':
            start_time = flight.ttot - 600
        else:
            start_time = flight.aldt

        sour, des = Sour_and_Des.find_the_sour_des(stands=stand_dict, pists=runway_dict, flight=flight)

        # using the general example to test
        # source_flight = [155, 86]
        # des_flight = [170, 164]
        # sour = source_flight[flightnum]
        # des = des_flight[flightnum]

        path, path_coord, path_activation_times, cost = find_routing(the_airport, the_airport2, sour, des, flight, flightnum, network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo, node_lock_periods, start_time)

        activation_times_list.append(path_activation_times)
        pathlist.append(path)
        path_coordlist.append(path_coord)

        get_node_lock_periods(pathlist, activation_times_list, network_cepo, flight, node_lock_periods)

        costs.append(cost)
        Total_COST = Total_COST +cost

        lenth = 0
        time_lenth = 0
        turn_time = 0
        for i in range(1, len(path_coord)):
            current_vertex = path_coord[i - 1]
            next_vertex = path_coord[i]
            edge = (current_vertex, next_vertex)
            # print(weights[edge])
            l = init_l[edge]
            t = network[current_vertex][next_vertex]
            if l <= 0:
                turn_time += 1
            lenth = lenth + abs(l)
            time_lenth = time_lenth + t
        turn_times = turn_times + turn_time
        Lenth = Lenth + lenth
        Tcost_without_waiting = Tcost_without_waiting + time_lenth

        # print('flightnum', flightnum,'path', path)
        print('flightnum', flightnum, "Cost:", cost)
        print('path', path_coord)
        print(lenth, time_lenth, turn_time)

    costs.append(Total_COST)
    costs.append(Lenth)
    costs.append(Tcost_without_waiting)
    costs.append(turn_times)
    print('Total cost', Total_COST)
    print("Lenth:", Lenth, "Tcost_without_waiting:", Tcost_without_waiting, "Total_turn_times ", turn_times)
    # # 确保目录存在
    # file = Cst.file
    # os.makedirs(file, exist_ok=True)
    write_list_to_file(costs, Cst.file0 + 'Cost' + '.txt')

    # 现在我们可以调用这些函数将列表写入到文本文件
    # write_list_to_file(pathlist, 'saved_figures_gaptraffic-2019-08-07-new/pathlist.txt')
    # write_list_to_file(path_coordlist, 'saved_figures_gaptraffic-2019-08-07-new/path_coordlist.txt')
    # write_list_to_file(activation_times_list, 'saved_figures_gaptraffic-2019-08-07-new/activation_times_list.txt')
    #
    # # 现在我们可以调用这些函数将列表写入到json文件
    # write_list_to_json(pathlist, 'saved_figures_gaptraffic-2019-08-07-new/pathlist.json')
    # write_list_to_json(path_coordlist, 'saved_figures_gaptraffic-2019-08-07-new/path_coordlist.json')
    # write_list_to_json(activation_times_list, 'saved_figures_gaptraffic-2019-08-07-new/activation_times_list.json')

    # Find_Routing_for_test.find_routing(the_airport, t he_airport2)


