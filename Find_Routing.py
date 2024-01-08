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


def find_routing(the_airport, the_airport2, sour, des, flight, flightnum, network, pointcoordlist, network_cepo,
             in_angles, out_angles, in_angles_cepo, out_angles_cepo, node_lock_periods):

    # 单架飞机规划路径：
    # network_point, x, y, pointcoordlist, network = findpath.findRSApath(the_airport2)
    # s0 = findpath.findsource(points=the_airport2.points)
    # d0 = findpath.finddes(points=the_airport2.points)
    # s = pointcoordlist.index(s0)
    # # s = 12
    # d = pointcoordlist.index(d0)
    # orad = 500  # obstacle radius
    # ospeed = 2  # obstacle speed
    # (RSA4CEPO2.main(network, s, d, x, y, orad, ospeed, pointcoordlist, the_airport2, network_point))

    # 多飞机规划路径：
    # 初始化开始时间

    if flight.departure == 'ZBTJ':
        start_time = flight.ttot - 600
    else:
        start_time = flight.aldt

    # start_time = 0

    # 为当前飞机规划路径
    # network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo \
    #     = Initial_network.initial_network(the_airport2)

    # flightnum = len(pathlist) + 1
    s = pointcoordlist.index(sour)
    d = pointcoordlist.index(des)
    # source_flight = [155, 86]
    # des_flight = [170, 164]
    # s = source_flight[flightnum]
    # d = des_flight[flightnum]
    # if len(pathlist) != 0:
    #     path = pathlist[-1]
    #     block_timedict = helpfunction.blocknode(network_cepo, path, start_time)
    #     blockinfo[flightnum - 1] = block_timedict
    #     block_timedict2 = helpfunction.blocknode2(network_cepo, path, start_time)
    #     blockinfo2[flightnum - 1] = block_timedict2

    """CEPO 寻路过程"""
    path_set, length_set, plist, t, v, path_activation_times = \
        RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d, flightnum, pointcoordlist,
                       the_airport2, network, start_time, node_lock_periods, the_airport2.points)

    # print("Flightnum :", flightnum)
    # print('shortest path:', path_set, 'length:', length_set)

    # pathlist.append(path_set)
    # print("pathlist",pathlist)
    # path_coordlist.append(plist)

    # Draw_path.create_matplotlib_figure(network_point=network, pointcoordlist=pointcoordlist, path=plist, stand=s,
    #                                    runway=d, flightnum=flightnum)

    return path_set, plist, path_activation_times

    # Draw_path.create_matplotlib_figure0(network, pointcoordlist, path=[], stand=34, runway=2)

    # 这里我们考虑多架飞机的情况
    # for flightnum in range(1):
        # start_time = init_time + datetime.timedelta(seconds=10 * flightnum)
        # 随机选择起点和终点
        # s = pointcoordlist.index(sour)
        # d = pointcoordlist.index(des)

        # # 为当前飞机规划路径
        # network, x, y, pointcoordlist, network = findpath.findRSApath(the_airport2, blocked_points)
        # s = pointcoordlist.index(source)
        # d = pointcoordlist.index(destination)


        # if flightnum != 0:
        #     path = pathlist[-1]
        #     block_timedict = helpfunction.blocknode(network_cepo, path, start_time)
        #     blockinfo[flightnum - 1] = block_timedict
        #     block_timedict2 = helpfunction.blocknode2(network_cepo, path, start_time)
        #     blockinfo2[flightnum - 1] = block_timedict2

        # path_set, length_set, plist, t, v = RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d,
        #                                                    flightnum, pathlist, pointcoordlist, the_airport2, network,
        #                                                    start_time, blockinfo, points=the_airport2.points)
        # print("Flightnum :", flightnum)
        # print('shortest path:', path_set, 'length:', length_set)

        # 更新blocked_points，考虑当前飞机的位置和前一架飞机的位置
        # ... 省略更新blocked_points的代码

        # pathlist.append(path_set)
        # path_coordlist.append(plist)

        # 暂停20秒
        # time.sleep(10)

        # 更新开始时间
        # start_time += datetime.timedelta(seconds=10)
        # Draw.create_bokeh_animation(network, network_cepo, pointcoordlist, t, v, plist)
        # Draw_path.create_matplotlib_figure(network_point=network, pointcoordlist=pointcoordlist, path=plist, stand=s, runway=d)
    # Draw_path.create_bokeh_animation_with_paths(network, network_cepo, pointcoordlist, v, t, pathlist, plist,
    #                                             blockinfo2, path_coordlist)



