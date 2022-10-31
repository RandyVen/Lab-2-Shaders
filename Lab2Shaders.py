
from gl import Render

r = Render()
r.glInit(800,600)

r.load('./sphere.obj', [1, 1, 1], [300, 300, 300])

r.glFinish('Planeta.bmp')