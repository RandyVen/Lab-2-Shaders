# Randy Venegas 18341
# Graficas por Computadora 

import struct
import random
from obj import Obj, Texture
from collections import namedtuple

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def char(input):
	return struct.pack('=c', input.encode('ascii'))

def word(input):
	return struct.pack('=h', input)

def dword(input):
	return struct.pack('=l', input)

def glColor(r, g, b):
	return bytes([b, g, r])

def cross(v1, v2):
	return V3(
		v1.y * v2.z - v1.z * v2.y,
		v1.z * v2.x - v1.x * v2.z,
		v1.x * v2.y - v1.y * v2.x,
	)

def bbox(*vertices):
	xs = [ vertex.x for vertex in vertices]
	ys = [ vertex.y for vertex in vertices]

	xs.sort()
	ys.sort()


	xmin = xs[0]
	ymin = ys[0]
	xmax = xs[-1]
	ymax = ys[-1]

	return xmin, xmax, ymin, ymax

def barycentric(A, B, C, P):
	cx, cy, cz = cross(
		V3(C.x - A.x, B.x - A.x, A.x - P.x), 
		V3(C.y - A.y, B.y - A.y, A.y - P.y)
	)

	if abs(cz) < 1:
		return -1, -1, -1

	u = cx/cz
	v = cy/cz
	w = 1 - (u + v)

	return V3(w, v, u)


def sum(v0, v1):
	return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
	return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
	return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
	return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):
	return V3(
		v0.y * v1.z - v0.z * v1.y,
		v0.z * v1.x - v0.x * v1.z,
		v0.x * v1.y - v0.y * v1.x,
	)

def length(v0):
	return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):

	v0length = length(v0)

	if not v0length:
		return V3(0, 0, 0)

	return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

BLACK = glColor(0, 0, 0)

class Render(object):
	def glInit(self, width, height):
		self.width = width
		self.height = height
		self.color = glColor(255, 255, 255)
		self.clearColor = glColor(0, 0, 0)
		self.glClear()

		self.zbuffer = [
			[-float('inf') for x in range(self.width)]
			for y in range(self.height)
		]

	def glColorPoint(self, r, g, b):
		self.color = glColor(round(r * 255), round(g * 255), round(b * 255))

	def glCreateWindow(self, width = 640, height = 480):
		self.width = width
		self.height = height

	def glClear(self):
		self.framebuffer = [
			[BLACK for i in range(self.width)]
			for j in range(self.height)
		]

		self.zbuffer = [
			[-float('inf') for x in range(self.width)]
			for y in range(self.height)
		]

	def glClearColor(self, r, g, b):
		self.clearColor = glColor(round(r * 255), round(g * 255), round(b * 255))
		self.framebuffer = [
            [clearColor for x in range(self.width)] for y in range(self.height)
        ]

	def pixel(self, x, y, color):
		try:
			self.framebuffer[y%self.height][x%self.width] = color
		except:
			pass

	def glFinish(self, filename):
		f = open(filename, 'bw')

		f.write(char('B'))
		f.write(char('M'))
		f.write(dword(54 + self.width * self.height * 3))
		f.write(dword(0))
		f.write(dword(54))

		f.write(dword(40))
		f.write(dword(self.width))
		f.write(dword(self.height))
		f.write(word(1))
		f.write(word(24))
		f.write(dword(0))
		f.write(dword(self.width * self.height * 3))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))

		for x in range(self.height):
			for y in range(self.width):
				f.write(self.framebuffer[x][y])

		f.close()

	def glLine(self, A, B, color):

		x1 = A.x
		y1 = A.y
		x2 = B.x
		y2 = B.y

		dy = abs(y2 - y1)
		dx = abs(x2 - x1)
		steep = dy > dx

		if steep:
		    x1, y1 = y1, x1
		    x2, y2 = y2, x2

		if x1 > x2:
		    x1, x2 = x2, x1
		    y1, y2 = y2, y1

		dy = abs(y2 - y1)
		dx = abs(x2 - x1)

		offset = 0
		threshold = dx

		y = y1
		for x in range(x1, x2 + 1):
		    if steep:
		        self.pixel(y, x, color)
		    else:
		        self.pixel(x, y, color)
		    
		    offset += dy * 2
		    if offset >= threshold:
		        y += 1 if y1 < y2 else -1
		        threshold += dx * 2

	def transform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
    
	    return V3(
	      	round((vertex[0] + translate[0]) * scale[0]),
	      	round((vertex[1] + translate[1]) * scale[1]),
	      	round((vertex[2] + translate[2]) * scale[2])
	    )

	def load(self, filename, translate, scale, texture = None):
		model = Obj(filename)

		light = V3(0,0,1)

		for face in model.faces:
			
			vcount = len(face)

			vertices = []
			tvertices = []

			for j in range(vcount):
				f1 = face[j][0] - 1

				v1 = model.vertices[f1]

				x1 = round((v1[0] + translate[0]) * scale[0])
				y1 = round((v1[1] + translate[1]) * scale[1])
				z1 = round((v1[2] + translate[2]) * scale[2])

				

				vertices.append(V3(x1, y1, z1))

				f1t = face[j][1] - 1
				v1t = model.tvertices[f1t]
				tvertices.append(V2(v1t[0], v1t[1]))


			randomColor = glColor(random.randint(0,255),random.randint(0,255),random.randint(0,255))	

			A = vertices[0]
			B = vertices[1]
			C = vertices[2]

			normal = norm(cross(sub(B, A), sub(C, A)))
			intensity = dot(normal, light)
			grey = round(255 * intensity)
			if grey < 0:
				continue

			
			tA = vertices[0]
			tB = vertices[1]
			tC = vertices[2]

			self.triangle(
				vertices=(A,B,C),
			 	tvertices=(tA, tB, tC),
			 	texture=texture
			 	
		 	)

			

	def shader(self, x, y):
		bloque = int(y/3)
		xLevel = x/self.width
		if(bloque%5 == 0):
			return glColor(0,40*3,int(250*xLevel))
		if(bloque%5 == 1):
			return glColor(0,30*3,int(230*xLevel))
		if(bloque%5 == 2):
			return glColor(0,20*3,int(210*xLevel))
		if(bloque%5 == 3):
			return glColor(0,30*3,int(230*xLevel))
		if(bloque%5 == 4):
			return glColor(0,40*3,int(250*xLevel))
		
		

	def triangle(self, vertices=(), tvertices=(), texture=None):
		A, B, C = vertices
		tA, tB, tC = tvertices

		xmin, xmax, ymin, ymax = bbox(A, B, C)

		for x in range(xmin, xmax + 1):
			for y in range(ymin, ymax + 1):
				P = V2(x, y)
				w, v, u = barycentric(A, B, C, P)
				if w < 0 or v < 0 or u < 0:
					
					continue

				z = A.z * w + B.z * v + C.z * u

				tx = tA.x * w + tB.x * v + tC.x * u
				ty = tA.y * w + tB.y * v + tC.y * u
				

				color = self.shader(x, y)

				if z > self.zbuffer[x][y]:
					self.pixel(x, y, color)
					self.zbuffer[x][y] = z
