import numpy as np
from affine import Affine
import warnings

# add static property support
class classproperty(property):
    pass


class classinstanceproperty(property):
    pass

class StaticProperty(type):
    def __new__(self, name, bases, props):
        class_properties = {}
        to_remove = {}
        for key, value in props.items():
            if isinstance(value, (classproperty, classinstanceproperty)):
                class_properties[key] = value
                if isinstance(value, classproperty):
                    to_remove[key] = value

        for key in to_remove:
            props.pop(key)

        HoistMeta = type('HoistMeta', (type,), class_properties)
        return HoistMeta(name, bases, props)

       

class DefaultLayout(metaclass=StaticProperty): 
  """
  DefaultLayout 

  Default layout, similar to the GCCMX layout but only one center button for start.
  """

  right_homerow_coords = [(-26.15, -11.75), (0,0), (26.65, -3.2), (53.3, -19.45), 
                          (-26.15, -33.75), (0, -22), (26.65, -25.2), (53.3, -41.45)]
    
  # the four buttons for directionals is just the first 4 buttons reflected along the Y axis
  left_homerow_coords = np.dot(right_homerow_coords[4:], [[-1, 0], [0, 1]])
    
  right_thumb_coords = [(0,0), (-18.5, -12.75), (0, 25.5), (-18.5, 12.75), (18.5, 12.75)]
  # modifier buttons are just the first two cstick buttons reflected along the Y axis
  left_thumb_coords = np.dot(right_thumb_coords[:2], [[-1, 0], [0, 1]])
  misc_coords = [(0,0)]

  right_homerow_affine = Affine.translation(100, 58)
  left_homerow_affine = Affine.translation(-100, 58)
  left_thumb_affine = Affine.translation(-70, -45)
  right_thumb_affine = Affine.translation(70, -45)
  misc_affine = Affine.translation(0, 18)

  @classproperty
  def layout(self): 
    # concat them to return the complete list
    coords = [self.left_homerow_layout, 
                      self.right_homerow_layout, 
                      self.left_thumb_layout, 
                      self.right_thumb_layout, 
                      self.misc_layout]
    coords = [c for c in coords if len(c)]
    
    return np.concatenate(coords, axis=0)


  @classproperty
  def tolist(self):
    return self.layout.tolist()

  
  @classproperty
  def __iter__(self):
    return self.layout.tolist().__iter__


  @classproperty
  def __next__(self):
    return self.layout.tolist().__next__


  @classproperty
  def left_homerow_layout(self): 
    assert len(np.asarray(self.left_homerow_coords).shape) == 2
    return [self.left_homerow_affine * c for c in self.left_homerow_coords]


  @classproperty
  def right_homerow_layout(self): 
    assert len(np.asarray(self.right_homerow_coords).shape) == 2
    return [self.right_homerow_affine * c for c in self.right_homerow_coords]


  @classproperty
  def left_thumb_layout(self): 
    assert len(np.asarray(self.left_thumb_coords).shape) == 2
    return [self.left_thumb_affine * c for c in self.left_thumb_coords]


  @classproperty
  def right_thumb_layout(self): 
    assert len(np.asarray(self.right_thumb_coords).shape) == 2
    return [self.right_thumb_affine * c for c in self.right_thumb_coords]


  @classproperty
  def misc_layout(self): 
    if len(self.misc_coords) == 0:
      return []
    assert len(np.asarray(self.misc_coords).shape) == 2
    return [self.misc_affine * c for c in self.misc_coords]


class GccmxLayout(DefaultLayout):
  """
  GccmxLayout A layout mimicing Crane's GCCMX layout

  This is the same as the default layout except there are 
  three buttons in the center to suppport things like a home and share buttons 
  when combining a brook with a ModelS.
  """
  misc_coords = [(-20, 0), (0,0), (20, 0)]


