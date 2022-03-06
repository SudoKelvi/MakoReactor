import cadquery as cq
import alphashape as alph

import warnings

import numpy as np
from scipy.ndimage import affine_transform

from makogen import DefaultLayout

# inches to mm conversion 
in2mm = lambda x: x*25.4

# get a zip object as a list, syntax sugar
lzip = lambda *args, **kwargs: list(zip(*args, **kwargs)) 


def get_poly_verts(poly):
  verts = poly.vertices().vals()
  coords_x = [v.X for v in verts]
  coords_y = [v.Y for v in verts]
  return coords_x, coords_y


class StackedLeverless():
  def __init__(self,
               width = in2mm(14),
               height = in2mm(6),
               depth = 5,
               layout=DefaultLayout,
               hole_diameter = 8,
               hole_offset = 25,
               hole_deltax = 275,
               hole_deltay = 275,
               fillet_radius = 11):
   
    self.layout = layout
    self.width = width
    self.height = height
    self.depth  = depth
    self.hole_diameter = hole_diameter
    self.hole_offset = hole_offset
    self.hole_deltax = hole_deltax
    self.hole_deltay = hole_deltay
    self.fillet_radius = fillet_radius


  def base(self):
    """
    create_base _summary_
    
    _extended_summary_
    
    Parameters
    ----------
    width : _type_, optional
        _description_, by default in2mm(14.5)
    height : _type_, optional
        _description_, by default in2mm(7)
    depth : int, optional
        _description_, by default 5
    hole_diameter : int, optional
        _description_, by default 8
    hole_offset : int, optional
        _description_, by default 25
    hole_deltax : int, optional
        _description_, by default 300
    hole_deltay : int, optional
        _description_, by default 300
    fillet_radius : int, optional
        _description_, by default 5
    
    Returns
    -------
    _type_
        _description_
    """
    center_hole_spacing = 50 
    
    # base 
    base = cq.Workplane('XY').box(self.width, self.height, self.depth).edges("|Z").fillet(self.fillet_radius)
    
    width_left = self.width - self.hole_offset
    while width_left > self.hole_diameter or width_left == 0:
        base = base.faces(">Z").rect(width_left, self.height-self.hole_offset, forConstruction=True).vertices().hole(self.hole_diameter, self.depth*2)
        width_left -= self.hole_deltax
    
    height_left = self.height - self.hole_offset
    while height_left > self.hole_diameter or height_left == 0:
        print("cutting: ", height_left)
        base = base.faces(">Z").rect(self.width-self.hole_offset, height_left, forConstruction=True).vertices().hole(self.hole_diameter, self.depth*2)
        height_left -= self.hole_deltay
    
    return base


def create_switchplate(base, coords=DefaultLayout.layout, switch_mount_dimensions=(14,14)):
  # TODO: Error checking? Might be worth checking if the layout is in the bounda
  switch_plate = base.faces(">Z").pushPoints(coords).rect(*switch_mount_dimensions).cutThruAll()
  return switch_plate


def create_f1cap_faceplate(base, layout=DefaultLayout, cap_diameter=22.5, fillet=1, depth=10e9):
  """
  create_f1cap_faceplate _summary_

  _extended_summary_

  Parameters
  ----------
  base : _type_
      _description_
  layout : _type_, optional
      _description_, by default DefaultLayout
  cap_diameter : float, optional
      _description_, by default 22.5
  fillet : int, optional
      _description_, by default 1
  depth : _type_, optional
      _description_, by default 10e9
  """
  def generate_sketch(coords):
    s = (
        cq.Sketch()
        .push(list(coords))
        .circle(cap_diameter/2) # .circle uses radius for some reason
        .clean()
    )

    if fillet > 0:
      try:  
        s = s.reset().vertices().fillet(fillet)
      except Exception as e:
        pass # no edges to fillet
    return s 

  if hasattr(layout, "__iter__"): # this is some iterable
    # try to cut the complete layout 
    sketch = generate_sketch(layout)
    polys = cq.Workplane("XY").placeSketch(sketch).extrude(depth, both=True)
    return base.cut(polys)

  # assume it's a layout class
  sketches = [generate_sketch(l) for l in [layout.left_homerow_layout, 
                                           layout.right_homerow_layout, 
                                           layout.left_thumb_layout, 
                                           layout.right_thumb_layout, 
                                           layout.misc_layout]]
  
  polys = cq.Workplane().placeSketch(*sketches).extrude(depth, both=True)
  return base.cut(polys)