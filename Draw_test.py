import json
import gaptraffic
from bokeh.models import ColumnDataSource, Slider, Button
from bokeh.layouts import column
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.plotting import show
from bokeh.io import save
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
import airport
import os.path
import geo
import Initial_network

# 函数，从json文件读取列表
def read_list_from_json(filename):
    with open(filename, 'r') as f:
        list_name = json.load(f)
    return list_name


def write_list_to_json(list_name, filename):
    with open(filename, 'w') as f:
        json.dump(list_name, f)

DATA_PATH = "DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
airport_cepo: airport.Airport = airport.load2(APT_FILE)
airport_init: airport.Airport = airport.load(APT_FILE)

# 现在我们可以调用这个函数从json文件中读取列表
pathlist = read_list_from_json('saved_figures_gaptraffic-2019-08-07-new/pathlist.json')
path_coordlist = read_list_from_json('saved_figures_gaptraffic-2019-08-07-new/path_coordlist.json')
activation_times_list = read_list_from_json('saved_figures_gaptraffic-2019-08-07-new/activation_times_list.json')

# 打印读取的列表
# print("Path list: ", pathlist)
# print("Path Coord list: ", path_coordlist)
# print("Activation Times list: ", activation_times_list)

filename = "D:\\BBS_WORK_SPACE\\Python_Workspace\\Dynamic_Routing\\airport\\traffic\\gaptraffic-2019-08-07-new.csv"
flights = gaptraffic.read_flights(filename)
network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo = Initial_network.initial_network(airport_cepo)
start_times = []
for flight in flights:
    if flight.departure == 'ZBTJ':
        start_time = flight.ttot - 600
    else:
        start_time = flight.aldt
    start_times.append(start_time)

# Add the start time of each flight to the activation times of its nodes
for i in range(len(activation_times_list)):
    for j in range(len(activation_times_list[i])):
        activation_times_list[i][j] += start_times[i]

write_list_to_json(activation_times_list, 'saved_figures_gaptraffic-2019-08-07-new/activation_times_list_new.json')


def draw_network(p, network):
    xs = []
    ys = []
    for node, neighbors in network.items():
        for neighbor in neighbors:
            xs.append([node[0], neighbor[0]])
            ys.append([node[1], neighbor[1]])
    p.multi_line(xs, ys, color='gray',line_alpha=0.7, line_width=1)
    # x_coords = [coord[0] for coord in pointcoordlist]
    # y_coords = [coord[1] for coord in pointcoordlist]
    # p.circle(x=x_coords, y=y_coords, size=5, color='blackgrey', legend_label="Nodes")

def modify_doc(doc):
    colors = ['red', 'green', 'blue', 'purple', 'orange', 'pink', 'black']

    p = figure(title="Flight Paths", width=900, height=600)

    path_sources = []
    flightrate = [360, 380]
    last_active_times = [0] * len(path_coordlist[flightrate[0]:flightrate[1]])  # Track the last active time for each path
    for flightnum, path_coords in enumerate(path_coordlist[flightrate[0]:flightrate[1]]):  # Only take the paths from 220 to 260
        path_source = ColumnDataSource(data=dict(x=[], y=[]))
        path_sources.append(path_source)
        p.line(x='x', y='y', line_color=colors[flightnum % len(colors)], line_width=3, source=path_source)

    # Add network information
    draw_network(p, network)

    first_activation_time = activation_times_list[flightrate[0]][0]  # Assuming the first path is not empty

    def update():
        time = slider.value
        for flightnum, path_coords in enumerate(path_coordlist[flightrate[0]:flightrate[1]]):  # Only take the paths from 220 to 260
            active_coords = [coords for coords, activation_time in zip(path_coords, activation_times_list[flightnum+flightrate[0]]) if
                             activation_time <= time]
            if active_coords:
                last_active_times[flightnum] = time  # Update the last active time
            elif time - last_active_times[flightnum] > 20:
                active_coords = []  # Clear the path if it's been inactive for more than 20 seconds
            path_sources[flightnum].data = dict(x=[coord[0] for coord in active_coords],
                                                y=[coord[1] for coord in active_coords])

    slider = Slider(start=first_activation_time, end=max(max(times) for times in activation_times_list[flightrate[0]:flightrate[1]]), value=first_activation_time, step=1, title="Time")
    slider.on_change('value', lambda attr, old, new: update())

    doc.add_root(column(p, slider))
    doc.add_periodic_callback(update, 1000)

handler = FunctionHandler(modify_doc)
app = Application(handler)

# Run the server
server = Server({'/': app}, num_procs=1)
server.start()
server.io_loop.add_callback(server.show, "/")  # open in browser
server.io_loop.start()




# from bokeh.io import output_file, save
# output_file("output.html")
# save(app)


# 展示应用
# show(app)


# your code to create a figure


