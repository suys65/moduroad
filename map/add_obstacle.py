import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
G = nx.read_graphml("data/network/graph.graphml")

# 장
obstacle_point = Point(37.37451, 126.645548)

pos = {node: (float(G.nodes[node]['x']), float(G.nodes[node]['y'])) for node in G.nodes()}

# 장애물 가까이에 있는 엣지 가중치 증가
def update_edge_weights(G, point, increment=5):
    nearest_edge = None
    min_distance = float('inf')

    # 엣지에 대한 반복 처리
    for u, v in G.edges():
        try:
            # LineString 객체 생성
            edge_line = LineString([pos[u], pos[v]])
            distance = point.distance(edge_line)
            if distance < min_distance:
                nearest_edge = (u, v)
                min_distance = distance
        except KeyError as e:
            # 위치 정보가 누락된 노드에 대한 처리
            print(f"Position information is missing for node: {e}")

    # 가장 가까운 엣지의 가중치 업데이트
    if nearest_edge:
        G[nearest_edge[0]][nearest_edge[1]]['length'] += increment
        return nearest_edge

modified_edge = update_edge_weights(G, obstacle_point)

# 변경된 엣지 중심의 네트워크 시각화
def plot_network_zoomed_on_edge(G, edge, buffer=0.01):
    if not edge:
        print("No edge modified.")
        return
    
    u, v = edge
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, node_color='blue', edge_color='grey', alpha=0.3)
    nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color='red', width=2)
    nx.draw_networkx_nodes(G, pos, nodelist=[u, v], node_color='red', node_size=100)
    
    # 확대 영역 설정
    edge_pos = [pos[u], pos[v]]
    minx = min(edge_pos, key=lambda x: x[0])[0] - buffer
    maxx = max(edge_pos, key=lambda x: x[0])[0] + buffer
    miny = min(edge_pos, key=lambda x: x[1])[1] - buffer
    maxy = max(edge_pos, key=lambda x: x[1])[1] + buffer
    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)
    plt.title("Zoomed View on Modified Edge")
    plt.show()

plot_network_zoomed_on_edge(G, modified_edge)