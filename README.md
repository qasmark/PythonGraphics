## 4D Hypercube Visualization with Spotlight and Shadow

This Python project visualizes a 4D hypercube (tesseract) using PyQt5 and PyOpenGL, featuring:

- **4D Rotations:** The hypercube rotates in 4D space using two rotation angles, visualized by projection onto 3D space.
- **Dynamic Lighting:** A spotlight illuminates the hypercube, enhancing its 3D perception.
- **Moving Shadow:** The hypercube casts a dynamic shadow on a ground plane, further emphasizing its 3D presence.
- **Smooth Animation:** The hypercube continuously rotates and scales, creating an engaging visual experience.

**Dependencies:**

- PyQt5
- PyOpenGL
- NumPy

```python
pip install PyQt5 PyOpenGL numpy
```

**Features in Detail:**

- **4D Rotation:** The `rotation_matrix_4d` function creates a 4D rotation matrix based on two input angles. This matrix is then applied to each vertex of the hypercube before projection.
- **Projection:** The `project_vertex` function projects a 4D point (vertex) onto 3D space using a perspective projection.
- **Spotlight:**  A spotlight is defined using `GL_LIGHT1` and positioned above the hypercube, creating a focused beam of light.
- **Shadow:** A simplified shadow effect is achieved by projecting the hypercube's vertices onto the ground plane and drawing its edges with a darker color.
- **Animation:** A `QtCore.QTimer` is used to update the rotation angles and scaling factor, triggering a redraw of the scene in each timer event. 

**Future Enhancements:**

- Implement user interaction (e.g., mouse controls for camera movement).
- Experiment with different 4D rotation axes and speeds.
- Enhance the shadow rendering with more advanced techniques. 
