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


def cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
                 in_angles_cepo, out_angles_cepo, sour, des):
    init_time = datetime.datetime(2023, 4, 17, 7, 0)
    pathlist = []  # 按照飞机的顺序储存飞机的节点序号路径
    path_coordlist = []  # 按照飞机的顺序储存飞机的节点坐标路径
    blockinfo = {}  # 与实际小时分钟计数
    blockinfo2 = {}  # 按照绝对时间计算
    # 随机选择起点和终点
    s = pointcoordlist.index(sour)
    d = pointcoordlist.index(des)
    flightnum = 0
    start_time = 0

    path_set, length_set, plist, t, v, path_activation_times = RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d,
                                                       flightnum, pathlist, pointcoordlist, the_airport2, network,
                                                       start_time, blockinfo, points=the_airport2.points)
    print('shortest path:', path_set, 'length:', length_set)

    # 更新blocked_points，考虑当前飞机的位置和前一架飞机的位置
    # ... 省略更新blocked_points的代码

    pathlist.append(path_set)
    path_coordlist.append(plist)

    # 暂停20秒
    time.sleep(10)

    # 更新开始时间
    # Draw.create_bokeh_animation(network, network_cepo, pointcoordlist, t, v, plist)
    Draw_path.create_matplotlib_figure(network_point=network, pointcoordlist=pointcoordlist, path=plist, stand=s,
                                       runway=d)


def find_routing(the_airport, the_airport2):
    # 为当前飞机规划路径
    network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo = \
        Initial_network.initial_network(the_airport2)

    """遍历所有的停机坪与跑道起飞点的位置是否存在可行解"""
    stand_dict, runway_dict, stand_list, stand_dict2, runway_list, runway_dict2 \
        = Sour_and_Des.stand_and_runway_points(points=the_airport2.points)
    # for i in range(46, len(stand_list)):
    #     sour = stand_list[i]
    #     if sour[1] >= 6926:
    #         B7 = runway_dict['B7']
    #         rp = [B7, (20155, 6926), (23610, 6926), (21057, 9026), (24108, 9026)]
    #         for j in range(len(rp)):
    #             des = rp[j]
    #             print("The process i=", i, " j=", j)
    #             cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
    #                          in_angles_cepo, out_angles_cepo, sour, des)
    #     else:
    #         A10 = runway_dict['A10']
    #         A1 = runway_dict['A1']
    #         rp2 = [A10, A1, (20155, 6926), (21057, 9026), (24108, 9026)]
    #         for j in range(len(rp2)):
    #             des = rp2[j]
    #             print("The process i=", i, " j=", j)
    #             cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
    #                          in_angles_cepo, out_angles_cepo, sour, des)

    """遍历所有的跑道起飞点与停机坪的位置是否存在可行解"""
    rl = ['B3', 'B4', 'A1', 'A5', 'W3', 'W7', 'W8', 'B6', 'B5', 'A10', 'A11']
    rlabove = ['B3', 'B4', 'B6', 'B5']
    rlbelow = ['A1', 'A5', 'A10', 'A11']
    for i in range(5, len(runway_list)):
        sour = runway_list[i]
        sourname = runway_dict2[sour]
        if sourname in rl:
            # for j in range(121, len(stand_list)):
            for j in range(0, len(stand_list)):
                des = stand_list[j]
                if stand_list[j][1] >= 6926 and (sourname in rlabove):
                    print("The arrive process1 i=", i, " j=", j)
                    cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
                                 in_angles_cepo, out_angles_cepo, sour, des)
                elif stand_list[j][1] < 6926 and (sourname in rlbelow):
                    print("The arrive process2 i=", i, " j=", j)
                    cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
                                 in_angles_cepo, out_angles_cepo, sour, des)
                elif (sourname not in rlabove) and (sourname not in rlbelow):
                    print("The arrive process3 i=", i, " j=", j)
                    cepo_process(network, pointcoordlist, network_cepo, in_angles, out_angles, the_airport2,
                                 in_angles_cepo, out_angles_cepo, sour, des)
