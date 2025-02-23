from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.api.client import SpeckleClient
from specklepy.api import operations
from specklepy.objects.base import Base
from specklepy.core.api.inputs.version_inputs import CreateVersionInput
import plotly.express as px
from specklepy.core.api.operations import serialize as core_serialize
from specklepy.serialization.base_object_serializer import BaseObjectSerializer
import pandas as pd
from specklepy.objects import Base


# Identify the Project and Model
project_id = "daeb18ed0a"
model_id = "aab87740df"

# Set up authentication and connection to server
client = SpeckleClient(host ="macad.speckle.xyz")
account = get_default_account()
client.authenticate_with_account(account)
transport = ServerTransport(project_id, client)

# Get a list of active projects
projects = client.active_user.get_projects(limit=3)
for project in projects.items:
    print(project.name)
    print(project.id)

# Get a specific Model by ID
my_model = client.model.get(model_id, project_id)
print(my_model.name)

# Get the Referenced Object ID of the latest Version
versions = client.version.get_versions(model_id, project_id)
referenced_obj_id = versions.items[0].referencedObject
# Receive the referenced object (speckle object!)
print("Fetching data from the server...")
objData = operations.receive(referenced_obj_id, transport)
# operatons.serialize
print("Got the data!")

# speckle_object = objData["@Building"]
# child_obj = speckle_object["@{0}"][0]

# print("Received Base object")

# obj_base = operations.serialize(child_obj)
# serializer = BaseObjectSerializer()
# obj_base = serializer.write_json(child_obj)

child_obj = objData

all_properties = child_obj.get_member_names()
typed_properties = child_obj.get_typed_member_names()
dynamic_properties = child_obj.get_dynamic_member_names()

print("Properties received")

obj = {}
for p in dynamic_properties:
    obj[p] = child_obj[p]

# Scatter plot of elements

vertices = []
# pointsGFfloor = obj['@Ground level'][0]['@Floors'].Vertices
# points1floor = obj['@1st level'][0]['@Floors'].Vertices
# points2floor = obj['@2nd level'][0]['@Floors'].Vertices
# points3floor = obj['@3rd level'][0]['@Floors'].Vertices
# pointsRoof = obj['@Roof floor'].Vertices

# for p in pointsGFfloor:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "GF floor slab"})
# for p in points1floor:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "1F floor slab"})
# for p in points2floor:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "2F floor slab"})
# for p in points3floor:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "3F floor slab"})
# for p in pointsRoof:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Roof floor slab"})

for element in obj["@Facade"]:
    for p in element.Vertices:
        vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Facade"})
for element in obj["@Floors"]:
    for p in element.Vertices:
        vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Floors"})
for element in obj["@Walls"]:
    for p in element.Vertices:
        vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Walls"})
for element in obj["@Stairs"]:
    for p in element.Vertices:
        vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Stairs"})
    
# for floor in obj:
#     if floor != "@Roof floor" and floor != "@Facade":
#         for p in obj[floor][0]["@Stairs"].Vertices:
#             vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Stairs"})
# for floor in obj:
#     if floor != "@Roof floor" and floor != "@Facade":
#         for wall in obj[floor][0]["@Walls"]:
#             for p in wall.Vertices:
#                 vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Walls"})
# for floor in obj:
#     if floor != "@Roof floor" and floor != "@Facade":
#         for p in obj[floor][0]["@Floors"].Vertices:
#             vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Floor slabs"})
# for p in obj['@Roof floor'].Vertices:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Roof floor"})
# print("Done!")

fig = px.scatter_3d(
    vertices,
    x="x",
    y="y",
    z="z",
    color="element",
    opacity=0.7,
    title="Element Vertices (m)",
)

fig.show()



