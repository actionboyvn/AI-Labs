from Connection import Connection
import csv
import math
import time
import random
INF = 1440
connections = dict()
stops = set()
coordinates = dict()
lines = dict()
def convertTimeToInt(time):
    return (int(time[0:2]) * 60 + int(time[3:5])) % 1440
def convertIntToTime(time):
    hh = str(int(time / 60))
    mm = str(time % 60)
    if (len(hh) == 1):
        hh = '0' + hh
    if (len(mm) == 1):
        mm = '0' + mm
    return hh + ":" + mm
def readData():
    with open('connection_graph.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header_read_done = False
        for row in csv_reader:
            if header_read_done:
                line = row[2]
                departure_time = convertTimeToInt(row[3])
                arrival_time = convertTimeToInt(row[4])
                start_stop = row[5]
                end_stop = row[6]
                start_stop_lat = float(row[7])
                start_stop_lon = float(row[8])
                end_stop_lat = float(row[9])
                end_stop_lon = float(row[10])
                connection_new = Connection(line, departure_time, arrival_time, start_stop, end_stop, start_stop_lat, start_stop_lon, end_stop_lat, end_stop_lon)
                if start_stop not in connections:
                    connections[start_stop] = []
                connections[start_stop].append(connection_new)
                stops.add(start_stop)
                stops.add(end_stop)
                if (start_stop not in coordinates):
                    coordinates[start_stop] = [start_stop_lat, start_stop_lon]
                if (end_stop not in coordinates):
                    coordinates[end_stop] = [end_stop_lat, end_stop_lon]
                if line in lines:
                    lines[line].add(start_stop)
                    lines[line].add(end_stop)
                else:
                    lines[line] = set()
            else:
                header_read_done = True
def tracePath(stopA, stopB, prev):
    if (stopB == stopA):
        return
    shortestPath = []
    while (prev[stopB].start_stop != stopA):
        shortestPath.append(prev[stopB])
        stopB = prev[stopB].start_stop
    shortestPath.append(prev[stopB])
    shortestPath.reverse()
    print("Solution found: ")
    for connection in shortestPath:
        print("Line " + connection.line + \
            ", start_stop: " + connection.start_stop + \
            ", end_stop: " + connection.end_stop + \
            ", departure_time: " + convertIntToTime(connection.departure_time) + \
            ", arrival_time: " + convertIntToTime(connection.arrival_time))
    print()        
def findShortestPathWithDijkstra(stopA, stopB, time_at_stopA):
    dist = dict()
    prev = dict()
    Q = set()
    for stop in stops:
        dist[stop] = INF
        Q.add(stop)
    dist[stopA] = 0
    while len(Q) > 0:
        u = ''
        for q in Q:
            if (u == '' or dist[q] < dist[u]):
                u = q     
        if u == stopB:
            print("Smallest traveling time: ", dist[stopB], " minute(s)")
            tracePath(stopA, stopB, prev)
            return
        Q.remove(u)
        if (u in connections):
            if (u == stopA):
                time_at_stop_u = time_at_stopA
            else:
                time_at_stop_u = prev[u].arrival_time
            for connection in connections[u]:
                v = connection.end_stop
                if (connection.departure_time >= time_at_stop_u or (time_at_stop_u >= 22 * 60 and connection.departure_time <= 2 * 60)):
                    if connection.departure_time >= time_at_stop_u:
                        time_fix = 0
                    else:
                        time_fix = 1440
                    if (dist[v] > dist[u] + connection.departure_time + time_fix - time_at_stop_u + abs(connection.arrival_time - connection.departure_time)):
                        dist[v] = dist[u] + connection.departure_time + time_fix - time_at_stop_u + abs(connection.arrival_time - connection.departure_time)
                        prev[v] = connection
    print("No solution found.")    
def findShortestPathWithAStar(stopA, stopB, time_at_stopA):
    h = dict()
    for stop in stops:
        h[stop] = math.sqrt((coordinates[stopB][0] - coordinates[stop][0])**2 + (coordinates[stopB][1] - coordinates[stop][1])**2)
    g = dict()
    f = dict()
    prev = dict()
    open_stops = set()
    closed_stops = set()
    for stop in stops:
        f[stop] = INF
        g[stop] = INF
    g[stopA] = 0
    f[stopA] = g[stopA] + h[stopA]
    open_stops.add(stopA)
    while (len(open_stops) > 0):
        chosen_stop = ''
        for stop in open_stops:
            if chosen_stop == '' or f[stop] < f[chosen_stop]:
                chosen_stop = stop    
        if (chosen_stop == stopB):
            print("Smallest traveling time: ", int(f[stopB]), " minute(s)")
            tracePath(stopA, stopB, prev)
            return
        open_stops.remove(chosen_stop)
        closed_stops.add(chosen_stop)
        if chosen_stop in connections:
            if chosen_stop == stopA:
                time_at_chosen_stop = time_at_stopA
            else:
                time_at_chosen_stop = prev[chosen_stop].arrival_time
            for connection in connections[chosen_stop]:
                next_stop = connection.end_stop
                if connection.departure_time >= time_at_chosen_stop or (time_at_chosen_stop >= 22 * 60 and connection.departure_time <= 2 * 60):
                    if connection.departure_time >= time_at_chosen_stop:
                        time_fix = 0
                    else:
                        time_fix = 1440
                    if (next_stop not in open_stops) and (next_stop not in closed_stops):
                        open_stops.add(next_stop)
                        g[next_stop] = g[chosen_stop] + connection.departure_time + time_fix - time_at_chosen_stop + abs(connection.arrival_time - connection.departure_time)
                        f[next_stop] = g[next_stop] + h[next_stop]
                        prev[next_stop] = connection
                    else:
                        if (g[next_stop] > g[chosen_stop] + connection.departure_time + time_fix - time_at_chosen_stop + abs(connection.arrival_time - connection.departure_time)):
                            g[next_stop] = g[chosen_stop] + connection.departure_time + time_fix - time_at_chosen_stop + abs(connection.arrival_time - connection.departure_time)
                            f[next_stop] = g[next_stop] + h[next_stop]
                            prev[next_stop] = connection
                            if next_stop in closed_stops:
                                open_stops.add(next_stop)
                                closed_stops.remove(next_stop)
    print("No solution found.")
def calcHeuristicsForTransferCriterion(stopB):
    h_transfer_criterion = dict()    
    for stop in stops:
        on_one_line_check = False
        for line in lines:
            if stop in lines[line] and stopB in lines[line]:
                h_transfer_criterion[stop] = 0
                on_one_line_check = True
                break
        if (not on_one_line_check):
            h_transfer_criterion[stop] = math.sqrt((coordinates[stopB][0] - coordinates[stop][0])**2 + (coordinates[stopB][1] - coordinates[stop][1])**2)        
    return h_transfer_criterion
def tracePathRecursive(stopA, prev, current_stop, current_line, current_transfers, required_transfers, accum):
    if stopA == current_stop and current_transfers == required_transfers:
        return accum
    if current_stop in prev:
        for prev_connection in prev[current_stop]:
            if prev_connection.line == current_line:
                transfer = 0
                accum_added = "Line " + prev_connection.line + \
                            ", start_stop: " + prev_connection.start_stop + \
                            ", end_stop: " + prev_connection.end_stop +\
                            ", departure_time: " + convertIntToTime(prev_connection.departure_time) + \
                            ", arrival_time: " + convertIntToTime(prev_connection.arrival_time) + "\n" + str(accum) 
                if (current_transfers + transfer <= required_transfers):
                    found = tracePathRecursive(stopA, prev, prev_connection.start_stop, prev_connection.line, current_transfers + transfer, required_transfers, accum_added)
                    if (len(found) > 0):
                        return found
        for prev_connection in prev[current_stop]:
            if prev_connection.line != current_line:
                transfer = 1
                accum_added = "Line " + prev_connection.line + \
                            ", start_stop: " + prev_connection.start_stop + \
                            ", end_stop: " + prev_connection.end_stop +\
                            ", departure_time: " + convertIntToTime(prev_connection.departure_time) + \
                            ", arrival_time: " + convertIntToTime(prev_connection.arrival_time) + "\n" + str(accum) 
                if (current_transfers + transfer <= required_transfers):
                    found = tracePathRecursive(stopA, prev, prev_connection.start_stop, prev_connection.line, current_transfers + transfer, required_transfers, accum_added)
                    if (len(found) > 0):
                        return found
    return ""
def tracePath2(stopA, stopB, prev, transfers):
    print("Solution found: ")
    if (stopB == stopA):
        return 
    else:
        print(tracePathRecursive(stopA, prev, stopB, '', 0, transfers, ""))
def filterDuplicatedConnections(connections_original):
    line_and_two_stops = set()
    connections_filtered = dict()
    for stop in stops:
        connections_filtered[stop] = []
        if stop in connections_original:
            for connection in connections_original[stop]:
                if not (connection.line, connection.start_stop, connection.end_stop) in line_and_two_stops:
                    line_and_two_stops.add((connection.line, connection.start_stop, connection.end_stop))
                    connections_filtered[stop].append(connection)
    return connections_filtered
def findShortestPathWithAStarAndTransferCriterion(stopA, stopB, modification_applied):
    h_transfer_criterion = calcHeuristicsForTransferCriterion(stopB)
    if modification_applied:
        connections_filtered = filterDuplicatedConnections(connections)
    else:
        connections_filtered = connections
    g = dict()
    f = dict()
    current_line = dict()
    current_line[stopA] = set()
    prev = dict()
    open_stops = set()
    closed_stops = set()
    for stop in stops:
        f[stop] = INF
        g[stop] = INF 
    g[stopA] = 0
    f[stopA] = g[stopA] + h_transfer_criterion[stopA]
    open_stops.add(stopA)
    while (len(open_stops) > 0):
        chosen_stop = ''
        for stop in open_stops:
            if chosen_stop == '' or (f[stop] < f[chosen_stop]):
                chosen_stop = stop      
        if chosen_stop == stopB:
            print("Number of total transfers: ", int(f[stopB]) - 1)
            tracePath2(stopA, stopB, prev, int(f[stopB]))
            return
        open_stops.remove(chosen_stop)
        closed_stops.add(chosen_stop)
        if chosen_stop in connections_filtered:         
            for connection in connections_filtered[chosen_stop]:
                stops_visited = set()
                if connection.end_stop != connection.start_stop:
                    current_stop = connection.start_stop
                    next_stop = connection.end_stop
                    current_connection = connection
                    connection_found = True                   
                    stops_visited.add(current_stop)
                    while (connection_found):     
                        stops_visited.add(next_stop)                    
                        if (current_stop in current_line and connection.line in current_line[current_stop]):
                            transfer = 0
                        else:
                            transfer = 1
                        if (g[next_stop] >= g[current_stop] + transfer):
                            if g[next_stop] > g[current_stop] + transfer:
                                if (next_stop in current_line):
                                    current_line[next_stop].clear()
                                else:
                                    current_line[next_stop] = set()
                                if (next_stop in prev):
                                    prev[next_stop].clear()
                                else:
                                    prev[next_stop] = []
                                open_stops.add(next_stop)
                            g[next_stop] = g[current_stop] + transfer
                            f[next_stop] = g[next_stop] + h_transfer_criterion[next_stop]                                                  
                            current_line[next_stop].add(connection.line)                                                        
                            prev[next_stop].append(current_connection)
                            stops_visited.add(next_stop)  
                        connection_found = False
                        if next_stop in connections_filtered:
                            for next_connection in connections_filtered[next_stop]:
                                if next_connection.line == connection.line and next_connection.end_stop not in stops_visited:
                                    current_stop = next_connection.start_stop
                                    next_stop = next_connection.end_stop
                                    current_connection = next_connection
                                    connection_found = True
                                    break
    print("No solution found.")    
def main():
    readData()
    while True:
        stopA = ""
        stopB = ""
        opt_criterion = "t"
        time_at_stopA = 0
        while True:
            stopA = input("Enter stop A: ")
            if (stopA in connections):
                break
            print("Stop A not found!")
        while True:
            stopB = input("Enter stop B: ")
            if (stopB in connections):
                break
            print("Stop B not found!")
        while True:
            opt_criterion = input("Optimization criterion ('t' or 'p'): ")
            if (opt_criterion in ["t", "p"]):
                break
            print("Wrong criterion format.")
        while True:
            time_string = input("Enter time at stop A (hh:mm): ")
            hh = time_string[0:2]
            mm = time_string[3:5]
            if (hh.isnumeric() and mm.isnumeric()):
                time_at_stopA = (int(time_string[0:2]) * 60 + int(time_string[3:5])) % 1440
                break
            print("Wrong time format.")
        while True:
            print("Choose an algorithm:")
            print("\t1. Dijkstra")
            print("\t2. A*")
            print("\t3. A* with modification for 'p' criterion")
            print("\t4. Re-enter input data")
            choice = input("Your choice: ")
            if (choice == "1" and opt_criterion == "t"):
                begin_time = time.time()
                findShortestPathWithDijkstra(stopA, stopB, time_at_stopA)
                end_time = time.time()
                print("Calculation time: %.4f s" % (end_time - begin_time))        
            elif choice == "2" and opt_criterion == "t":
                begin_time = time.time()
                findShortestPathWithAStar(stopA, stopB, time_at_stopA)
                end_time = time.time()
                print("Calculation time: %.4f s" % (end_time - begin_time))
            elif choice == "2" and opt_criterion == "p":
                begin_time = time.time()
                findShortestPathWithAStarAndTransferCriterion(stopA, stopB, False)
                end_time = time.time()
                print("Calculation time: %.4f s" % (end_time - begin_time))
            elif choice == "3" and opt_criterion == "p":
                begin_time = time.time()
                findShortestPathWithAStarAndTransferCriterion(stopA, stopB, True)
                end_time = time.time()
                print("Calculation time: %.4f s" % (end_time - begin_time))
            elif choice == "4":
                break         
            else:
                print("Please choose again")
            print()
def resultsCheck1():
    readData()
    list_of_stops = list(stops)
    stopA = ""
    stopB = ""
    time_at_stopA = 0
    timeout = time.time() + 30 * 60
    iteration_count = 0
    while True:
        if time.time() > timeout:
            break
        iteration_count += 1
        stopA = random.choice(list_of_stops)
        stopB = random.choice(list_of_stops)
        time_at_stopA = random.randrange(0, 1440)
        res_dijkstra = findShortestPathWithDijkstra(stopA, stopB, time_at_stopA)
        res_a_star = findShortestPathWithAStar(stopA, stopB, time_at_stopA)
        if (res_dijkstra != res_a_star):
            print(res_dijkstra, " ", res_a_star, " ", stopA, " ", stopB)
    print(iteration_count)
def resultsCheck2():
    readData()
    list_of_stops = list(stops)
    stopA = ""
    stopB = ""
    timeout = time.time() + 30 * 60
    iteration_count = 0
    while True:
        if time.time() > timeout:
            break
        iteration_count += 1
        stopA = random.choice(list_of_stops)
        stopB = random.choice(list_of_stops)        
        res_a_star_with_modification = findShortestPathWithAStarAndTransferCriterion(stopA, stopB, True)
        res_a_star_without_modification = findShortestPathWithAStarAndTransferCriterion(stopA, stopB, False)
        if (res_a_star_with_modification != res_a_star_without_modification):
            print(res_a_star_with_modification, " ", res_a_star_without_modification, " ", stopA, " ", stopB)
    print(iteration_count)
if __name__ == "__main__":
    main()
    #resultsCheck1()
    #resultsCheck2()
