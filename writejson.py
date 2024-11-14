import sys
import math

import freecad_utils

sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/bin')
sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/lib')
import FreeCAD
import Part
import json

# Paths to your files
file1_path = "C:/Users/Administrator/OneDrive - Pharos Marine/바탕 화면/1. Calix Engine Heater.FCStd"
file2_path = "C:/Users/Administrator/OneDrive - Pharos Marine/바탕 화면/2. 3-way solenoid valve.FCStd"

# Load files
doc1 = FreeCAD.openDocument(file1_path)
doc2 = FreeCAD.openDocument(file2_path)

# Assuming each document has a main body part named "Body"
body1 = doc1.getObject("Body")
body2 = doc2.getObject("Body")

# Load positioning and rotation data from JSON
with open("best_data.json", "r") as file:
    best_data = json.load(file)

# Apply position and rotation to body1
body1.Placement.Base = FreeCAD.Vector(*best_data["transfer_position1_body"])
# Set rotation for body1
rotation1 = FreeCAD.Rotation(
    FreeCAD.Vector(1, 0, 0), math.radians(best_data["transfer_rotation1_body"][0])
).multiply(
    FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.radians(best_data["transfer_rotation1_body"][1]))
).multiply(
    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.radians(best_data["transfer_rotation1_body"][2]))
)
body1.Placement.Rotation = rotation1

# Apply position and rotation to body2
body2.Placement.Base = FreeCAD.Vector(*best_data["transfer_position2_body"])
# Set rotation for body2
rotation2 = FreeCAD.Rotation(
    FreeCAD.Vector(1, 0, 0), math.radians(best_data["transfer_rotation2_body"][0])
).multiply(
    FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.radians(best_data["transfer_rotation2_body"][1]))
).multiply(
    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.radians(best_data["transfer_rotation2_body"][2]))
)
body2.Placement.Rotation = rotation2

# Recompute documents to apply changes
doc1.recompute()
doc2.recompute()

# Perform collision detection
shape1 = body1.Shape
shape2 = body2.Shape
collision = shape1.common(shape2)
print(collision.Volume)

# Function for collision check with tolerance

collision_volume=freecad_utils.check_collision(body1, body2)['volume']
print(
    f"Collision volume: {collision_volume:.4f} m^3"
)
if collision_volume:
    print(f"Collision detected with tolerance.")

else:
    print(f"No collision detected with tolerance.")
