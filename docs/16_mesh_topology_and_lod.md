# Mesh Topology, Polygon Budgets, and Level of Detail (LOD)

Mesh topology refers to the flow and arrangement of vertices, edges, and
faces (polygons) that make up a 3D model. Good topology is characterized
by an even distribution of quad-based polygons (faces with four sides)
and edge loops that follow the natural deformations of the object. This
is particularly crucial for animated assets, as poor topology will cause
the mesh to pinch or tear when bent by a skeletal rig.

When assembling polygons, 3D artists must also be mindful of the overall
polygon count. While film quality assets can afford millions of polygons,
real-time game engines require strict budget limits to maintain high
frame rates. Retopology is the process of drawing a new, low-polygon mesh
over a high-polygon sculpt to create an asset that is optimized for
interactive gameplay.

To render massive, complex 3D worlds without crashing the hardware, game
engines utilize Level of Detail (LOD) systems. An LOD system involves
creating multiple versions of a single 3D model, each with a decreasing
number of polygons and lower-resolution textures.

As the game's camera moves further away from the object, the engine
dynamically swaps the high-quality model for a lower-quality one. Because
the object is far away and takes up very few pixels on the screen, the
player cannot see the reduction in detail. This technique dramatically
reduces the rendering workload on the GPU, allowing developers to
populate environments with thousands of objects while maintaining a
smooth framerate.
