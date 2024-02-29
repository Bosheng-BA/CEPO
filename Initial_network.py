import RSA4CEPO2
import airport
import os.path
import geo
import random
import helpfunction


DATA_PATH = "Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
airport_cepo: airport.Airport = airport.load2(APT_FILE)
airport_init: airport.Airport = airport.load(APT_FILE)


def initial_network(airport_cepo):
    network = {}
    network_cepo = {}
    in_angles = {}
    out_angles = {}
    in_angles_cepo = {}
    out_angles_cepo = {}
    init_l = {}
    # print("the number of points", len(airport_cepo.points))
    # points, lines, runways = [], [], []
    points = airport_cepo.points
    runways = airport_cepo.runways
    lines = airport_cepo.lines
    init_lines = airport_init.lines
    points0 = airport_init.points

    for (i, point) in enumerate(points):
        network[point.xy] = {}
        # init_l[point.xy] = {}
        in_angles[point.xy] = {}
        out_angles[point.xy] = {}
    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        length = geo.length(line_init.xys)
        length_cepo = abs(length / line.speed)
        # p1 = (float(line_init.xys[0][0]), float(line_init.xys[0][1]))
        p11 = line_init.xys[0]
        p22 = line_init.xys[1]
        p33 = line_init.xys[-2]
        p44 = line_init.xys[-1]
        p1 = line.xys[0]
        p4 = line.xys[-1]

        """删掉了最小的0.1边缘值，加速搜索两倍"""
        # if length_cepo <= 0.25:
        #     print(length_cepo)

        if length_cepo == 0.1:
            print('Line = 0。1', line.oneway, line.taxiway, line.xys, length)
            continue

        if p1 == (22622, 7891):
            p1 = (22622, 7892)
            # xylist = []
            # xylist.append((22622, 7892))
            # xylist = line_init.xys
            length = length + 1
        elif p4 == (22622, 7891):
            p4 = (22239, 7602)
            length = length + 1

        if line.speed != 10:
            length = -length
        init_l[(p1, p4)] = length
        init_l[(p4, p1)] = length

        while length != 0.0:  # ignore the line with length '0'
            network[p1][p4] = length_cepo
            network[p4][p1] = length_cepo
            if line.speed < 0:  # Give the angle of every arc and reverse the pushback's outangle
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p44, p33)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
            else:
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p33, p44)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
            length = 0.0  # 注意浮点型
            if line.oneway:  # 处理路网单向路
                network[p4].pop(p1)

    for (i, runway) in enumerate(runways):
        p1 = runway.xys[0]
        p2 = runway.xys[1]
        length = geo.length(runway.xys)
        network[p1][p2] = length
        network[p2][p1] = length
        in_angles[p1][p2] = geo.angle_2p(p1, p2)
        out_angles[p1][p2] = geo.angle_2p(p1, p2)
        in_angles[p2][p1] = geo.angle_2p(p2, p1)
        out_angles[p2][p1] = geo.angle_2p(p2, p1)

    # print(network)
    pointcoordlist = list(network.keys())
    # 处理路网

    for i in range(len(pointcoordlist)):  # 形成以节点序号为名称的路网
        network_cepo[i] = {}
        in_angles_cepo[i] = {}
        out_angles_cepo[i] = {}
        listkey = list(network[pointcoordlist[i]].keys())
        for (j, keys) in enumerate(listkey):
            key = pointcoordlist.index(keys)
            # print(key)
            network_cepo[i][key] = network[pointcoordlist[i]][keys]
            in_angles_cepo[i][key] = in_angles[pointcoordlist[i]][keys]
            out_angles_cepo[i][key] = out_angles[pointcoordlist[i]][keys]


    # print(network_cepo)

    # print_network_info(network, points)
    """********* print network **********"""
    # neighbor_info = helpfunction.turn_network(network)
    # helpfunction.print_neighbor_info(neighbor_info, points)
    return network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo, init_l


# def findsource(points):
#     source_points = [p for p in points if p.ptype == 'Stand']
#     point = random.choice(source_points)
#     # point = points[-10]
#     print("Source:", point.ptype, point.name, point.xy)
#     source = point.xy
#     return source
#
#
# def finddes(points):
#     des_points = [p for p in points if p.ptype == 'Runway']
#     point = random.choice(des_points)
#     print("Destination:", point.ptype, point.name, point.xy)
#     des = point.xy
#     return des

