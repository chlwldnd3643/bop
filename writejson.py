import sys
import math
sys.path.append('C:/Program Files/FreeCAD 0.21/bin')
sys.path.append('C:/Program Files/FreeCAD 0.21/lib')

import FreeCAD
import Part
import json

# Paths to your files
file1_path = "C:/Users/Pharosmarine/Desktop/Calix Engine Heater.FCStd"
file2_path = "C:/Users/Pharosmarine/Desktop/2. 3-way solenoid valve.FCStd"

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
def check_collision_with_tolerance(obj1, obj2, doc1, doc2):
    """
    Check collision between two parts with higher precision.
    Args:
        obj1: First FreeCAD object.
        obj2: Second FreeCAD object.
    Returns:
        True if there is a collision, False otherwise
    """

    # Apply position and rotation to body1
    obj1.Placement.Base = FreeCAD.Vector(*best_data["transfer_position1_body"])
    # Set rotation for body1
    rotation1 = FreeCAD.Rotation(
        FreeCAD.Vector(1, 0, 0), math.radians(best_data["transfer_rotation1_body"][0])
    ).multiply(
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.radians(best_data["transfer_rotation1_body"][1]))
    ).multiply(
        FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.radians(best_data["transfer_rotation1_body"][2]))
    )
    obj1.Placement.Rotation = rotation1

    # Apply position and rotation to body2
    obj2.Placement.Base = FreeCAD.Vector(*best_data["transfer_position2_body"])
    # Set rotation for body2
    rotation2 = FreeCAD.Rotation(
        FreeCAD.Vector(1, 0, 0), math.radians(best_data["transfer_rotation2_body"][0])
    ).multiply(
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.radians(best_data["transfer_rotation2_body"][1]))
    ).multiply(
        FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.radians(best_data["transfer_rotation2_body"][2]))
    )
    obj2.Placement.Rotation = rotation2

    # Recompute documents to apply changes
    doc1.recompute()
    doc2.recompute()

    # Perform collision detection
    shape1 = obj1.Shape
    shape2 = obj2.Shape
    collision = shape1.common(shape2)
    common = obj1.Shape.common(obj2.Shape)
    return common.Volume

collision_volume=check_collision_with_tolerance(body1, body2)
if collision_volume:
    print(collision_volume)
    print(f"Collision detected with tolerance.")

else:
    print(f"No collision detected with tolerance.")
