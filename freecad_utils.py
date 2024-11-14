import math
import sys

sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/bin')
sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/lib')

import FreeCAD

def load_freecad_part(file_path):
    try:
        doc = FreeCAD.open(file_path)
        FreeCAD.setActiveDocument(doc.Name)
        return doc
    except Exception as e:
        print(f"Error loading part: {e}")
        return None
# Function to apply translation and rotation to an object
def apply_transformation(obj, translation, rotation):
    obj.Placement.Base = FreeCAD.Vector(*translation)

    # Apply rotation around X, Y, and Z axes individually
    rotation_x = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), rotation[0])  # X-axis rotation
    rotation_y = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), rotation[1])  # Y-axis rotation
    rotation_z = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rotation[2])  # Z-axis rotation
    # Combine the rotations
    combined_rotation = rotation_x * rotation_y * rotation_z
    obj.Placement.Rotation = combined_rotation


# Function to check for collision between two parts with tolerance consideration
def check_collision(obj1, obj2):
    """
    Check collision between two parts with higher precision.
    Args:
        obj1: First FreeCAD object.
        obj2: Second FreeCAD object.
    Returns:
        Dictionary containing collision volume and intersection status.
    """
    # Perform collision detection
    shape1 = obj1.Shape
    shape2 = obj2.Shape
    intersection = shape1.common(shape2).Volume

    return {
        'volume': intersection,
        'is_intersection': bool(intersection > 0)
    }
