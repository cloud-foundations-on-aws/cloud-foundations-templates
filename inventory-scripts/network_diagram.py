import boto3
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from collections import defaultdict
import numpy as np

# Retrieve all TGW attachments and associated VPCs across all regions
all_regions = [region['RegionName'] for region in boto3.client("ec2").describe_regions()["Regions"]]
graph = nx.Graph()
region_colors = {}
region_nodes = defaultdict(list)
patches = []

for region_name in all_regions:
    session = boto3.Session(region_name=region_name)
    ec2 = session.client("ec2")

    try:
        tgws = ec2.describe_transit_gateways()["TransitGateways"]
        attachments = ec2.describe_transit_gateway_attachments()["TransitGatewayAttachments"]
    except Exception:
        continue

    for tgw in tgws:
        tgw_id = tgw["TransitGatewayId"]
        name = next((tag["Value"] for tag in tgw.get("Tags", []) if tag["Key"] == "Name"), tgw_id)
        graph.add_node(tgw_id, label=name, region=region_name, type="TGW")
        region_nodes[region_name].append(tgw_id)

    for attachment in attachments:
        if attachment["ResourceType"] == "vpc":
            tgw_id = attachment["TransitGatewayId"]
            vpc_id = attachment["ResourceId"]
            vpc_name = next((tag["Value"] for tag in attachment.get("Tags", []) if tag["Key"] == "Name"), vpc_id)
            graph.add_node(vpc_id, label=vpc_name, region=region_name, type="VPC")
            graph.add_edge(tgw_id, vpc_id)
            region_nodes[region_name].append(vpc_id)

# Draw the network
pos = nx.spring_layout(graph, seed=42)
plt.figure(figsize=(14, 10))

for node, data in graph.nodes(data=True):
    node_color = "skyblue" if data["type"] == "TGW" else "lightgreen"
    region = data["region"]

    if region not in region_colors:
        region_colors[region] = plt.cm.tab10(len(region_colors))
        patches.append(mpatches.Patch(color=region_colors[region], label=region))

    nx.draw_networkx_nodes(graph, pos, nodelist=[node], node_color=node_color)

nx.draw_networkx_labels(graph, pos, labels={n: d["label"] for n, d in graph.nodes(data=True)}, font_size=8)
nx.draw_networkx_edges(graph, pos)

# Draw region clusters with ellipses
for region, nodes in region_nodes.items():
    node_positions = np.array([pos[node] for node in nodes if node in pos])
    if len(node_positions) > 1:
        x_center = np.mean(node_positions[:, 0])
        y_center = np.mean(node_positions[:, 1])
        width = (max(node_positions[:, 0]) - min(node_positions[:, 0])) * 1.4
        height = (max(node_positions[:, 1]) - min(node_positions[:, 1])) * 1.4
        ellipse = Ellipse((x_center, y_center), width, height,
                          edgecolor=region_colors[region], facecolor=region_colors[region],
                          alpha=0.1, zorder=0)
        plt.gca().add_patch(ellipse)

plt.legend(handles=patches)
plt.title("AWS TGW-VPC Network Map Clustered by Region")
plt.axis("off")
plt.show()
