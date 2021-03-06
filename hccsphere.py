#!/usr/bin/env python
# encoding: utf-8
"""
hccsphere.py

Created by Gruppo Biomedica 2010 2011
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from hasselib.graphLib6 import *
import numpy as np
from math import pi,sin,cos


DEBUG = True

#http://mathworld.wolfram.com/Octant.html
octant_sign = dict()
octant_sign[1] = lambda x : [1, abs(x[1]), abs(x[2]), abs(x[3])]
octant_sign[2] = lambda x : [1, -abs(x[1]), abs(x[2]), abs(x[3])]
octant_sign[3] = lambda x : [1, -abs(x[1]), -abs(x[2]), abs(x[3])]
octant_sign[4] = lambda x : [1, abs(x[1]), -abs(x[2]), abs(x[3])]
octant_sign[5] = lambda x : [1, abs(x[1]), abs(x[2]), -abs(x[3])]
octant_sign[6] = lambda x : [1, -abs(x[1]), abs(x[2]), -abs(x[3])]
octant_sign[7] = lambda x : [1, -abs(x[1]), -abs(x[2]), -abs(x[3])]
octant_sign[8] = lambda x : [1, abs(x[1]), -abs(x[2]), -abs(x[3])]



def minor(arr,i,j):
    # ith row, jth column removed
    return arr[np.array(range(i)+range(i+1,arr.shape[0]))[:,np.newaxis],
               np.array(range(j)+range(j+1,arr.shape[1]))]


def plane(matrix):
    d = np.linalg.det(minor(matrix,0,0))
    a = -np.linalg.det(minor(matrix,0,1))
    b = np.linalg.det(minor(matrix,0,2))
    c = -np.linalg.det(minor(matrix,0,3))
    return d,a,b,c


def intersect(plane1,plane2,plane3):
    A = np.array([plane1[1:],plane2[1:],plane3[1:]])
    b = np.array([[-plane1[0]],[-plane2[0]],[-plane3[0]]])
    A_inv = np.linalg.inv(A)
    return CAT([[1.0]] + np.dot(A_inv,b).tolist())


def reflect(point, i):
    """Given a point and its octant, reflect the points
    all along other octants."""

    return [octant_sign[oct](point) for oct in range(1,9) if oct != i]


def unique(alist):
    """Removes duplicates from a list."""
    
    no_dupes = []
    [no_dupes.append(i) for i in alist if not no_dupes.count(i)]
    return no_dupes


def neg(alist):
    return map(lambda x: -x, alist)
    

def cell(verts):
    def cell0(args):
        i,j,k = args
        return [index+1 for index,v in enumerate(verts) if AND([
            (GE(0) if i==1 else LE(0))(v[1]),
            (GE(0) if j==1 else LE(0))(v[2]),
            (GE(0) if k==1 else LE(0))(v[3]) ])]
    return cell0


#PASSO 1: Generare il politopo fondamentale
def sphere_kernel():
    
    g = Graph(3)

    i = [1,1,0,0]
    j = [1,0,1,0]
    k = [1,0,0,1]
    
    ij = [1.0, cos(pi/4), sin(pi/4), 0]
    jk = [1.0, 0, cos(pi/4), sin(pi/4)]
    ki = [1.0, cos(pi/4), 0, sin(pi/4)]
    zero = [1,0,0,0]

    mat_ij = np.array([zero,ki,i,ij])
    mat_jk = np.array([zero,ij,j,jk])
    mat_ki = np.array([zero,jk,k,ki])
    ijk = intersect(plane(mat_ij),plane(mat_jk),plane(mat_ki))

    #///////////////////////////////////////////////////////////////////////////
    # VERTICES
    #///////////////////////////////////////////////////////////////////////////
    #La numerazione dei vertici e' importante, convenzione:
    # 0 origine
    # 1,2,3 i,j,k
    # 4,5,6 -i, -j, -k
    # 7,8,9,10 nodi intermedi intorno a Z
    # 11,12,13,14 nodi intermedi intorno a X
    # 15, 16, 17, 18 nodi intermedi intorno a Y
    # 19,20,21,22,23,24,25,26 gli ijk sugli 8 quadranti.
    verts = [zero,i,j,k,neg(i),neg(j),neg(k)]
    along_z = [[1,cos(u), sin(u), 0] for u in np.arange(pi/4, 2*pi, pi/2)]
    along_x = [[1,0, cos(u), sin(u)] for u in np.arange(pi/4, 2*pi, pi/2)]
    along_y = [[1,cos(u), 0, sin(u)] for u in np.arange(pi/4, -3*pi/2, -pi/2)]

    verts += along_z
    verts += along_x
    verts += along_y

    verts += [ijk] + reflect(ijk, 1)
    
    for vert in verts:
        v = g.addNode(0); g.setVecf(v,Vecf(vert))


    if DEBUG:
        assert(len(CELLSPERLEVEL(g)(0)) == 27)


    #///////////////////////////////////////////////////////////////////////////
    # EDGES
    #///////////////////////////////////////////////////////////////////////////
    #"Umbrella" like edges (from origin). They are 6 [28, 34)
    edges = DISTL([0, range(1,7)])

    #A ring along z, same z. They are 8 [34..42)
    edges += zip([1,2,2,4,4,5,5,1], [7,7,8,8,9,9,10,10])

    #ring along x, same x. They are 8 [42..50)
    edges += zip([2,3,3,5,5,6,6,2], [11,11,12,12,13,13,14,14])

    #ring along y, same y. They are 8 [50, 58)
    edges += zip([3,1,1,6,6,4,4,3], [15,15,16,16,17,17,18,18])

    #superior octant 19,20,21,22. They are 8 [58,66) + 4 [66,70)
    edges += zip([15,11,11,18,18,12,12,15], [19,19,20,20,21,21,22,22])
    edges += zip([7,8,9,10], [19,20,21,22])
    
    #inferior octant 23,24,25,26. They are 8 [70,78) + 4 [78,82)
    edges += zip([16,14,14,17,17,13,13,16], [23,23,24,24,25,25,26,26])
    edges += zip([7,8,9,10], [23,24,25,26])


    for edge in edges:
        node = g.addNode(1); g.addArch(edge[0]+1,node);g.addArch(edge[1]+1,node)

    
    if DEBUG:
        assert(len(CELLSPERLEVEL(g)(1)) == 54)

    
    #///////////////////////////////////////////////////////////////////////////
    # FACETS
    #///////////////////////////////////////////////////////////////////////////
    #faces = [[28,29,34,35], [29, 30, 42, 43], [28,30,50,51]]

    #Facets with same z (z = 0)
    faces =  [[28,34,35,29], [29,36,37,31], [31, 38, 39, 32], [32, 40, 41, 28]]

    #Facets with same x (x = 0)
    faces += [[29,42,43,30], [30,44,45,32], [32, 46, 47, 33], [33, 48, 49, 29]]

    #Facets with same y (y = 0)
    faces += [[28,50,51,30], [28,52,53,33], [33,54,55,31], [31, 56, 57, 30]]

    for face in faces:
        node = g.addNode(2)
        for k in range(4): g.addArch(face[k],node)

    pols = AA(cell(verts))([[1,1,1],[-1,1,1],[1,-1,1],[1,1,-1],[-1,-1,1],[-1,1,-1],[1,-1,-1],[-1,-1,-1]])

    print cell(verts)([1,1,1])
    #///////////////////////////////////////////////////////////////////////////
    # 3-DIM SOLIDS
    #///////////////////////////////////////////////////////////////////////////
    for cll in pols:
        node = g.addNode(3)
        for vert in cll:
            g.addArch(node,vert)

            
    return g
        
    

#PASSO 2: Ricavare il bordo
def get_coords_from(g):
    def get_coords_from0(id):
        vect = g.getVecf(id)
        return [vect[0], vect[1], vect[2], vect[3]]

    return get_coords_from0


def exploded_points(g):
    def exploded_points0(id_list, expl_factor):
        coords_list = map(get_coords_from(g), id_list)
        result = [[el[0], expl_factor*el[1],
                   expl_factor*el[2],
                   expl_factor*el[3]] for el in coords_list]
        return result
    return exploded_points0
        
#NOTA
# Per evitare di generare due facce su due lati adiacenti di due casette,
# e' sufficiente fare un controllo sul livello 2 del grafo, partendo dagli
# spigoli (che sono in comune a 2 casette) e controllare risalendo il grafo
# se esiste qualcosa di livello 2: Se esiste non deve essere ridisegnato.

#PASSO 3.0: Per ogni quadrato del bordo, attacco una casetta
#PASSO 3.1: Raddoppio i vertici
#PASSO 3.2: Attacco gli spigoli
#PASSO 3.3: Genero i vertici aggiuntivi per il tetto
#PASSO 3.4: Chiudo la casetta
#PASSO 3.5: Con il graticcio di spigoli, genero gli spigoli


def graph2batches(g,expl=[1,1,1]):

    n = g.getMaxDimCells()
    m = g.getPointDim()

    def offset(point,expl=[1,1,1]):
        scaledpoint = [point[k]*expl[k] for k in range(3)]
        vect = VECTDIFF([scaledpoint,point])
        return vect
        

    def spheres(points,expl=[1,1,1]):
        batches = []
        sx = 0.05
        
        for point in points:
            batchSphere = get_sphere_batch().next()
            vect = offset(point,expl)
            if len(point) == 2:
                point = point + [0.0]
                vect = vect + [0.0]
            batchSphere.matrix =  Mat4f.translate(*vect) * \
                Mat4f.translate(*point)*Mat4f.scale(sx,sx,sx)
            batchSphere.diffuse=CYAN
            batches += [batchSphere]
        return batches


    def transfCylr(batchCylinder,pointpair,expl=[1,1,1]):
        vect,point = VECTDIFF(REVERSE(pointpair)),pointpair[0]
        sx = 0.025
        
        def vectTransform(vect):
            qz = UNITVECT(vect)
            qx = UNITVECT(VECTPROD([ vect,[0,0,1] ]))
            qy = VECTPROD([ qz,qx ])
            Rot = TRANS([qx,qy,qz]) 
            Rot = CAT([ Rot[0]+[0.], Rot[1]+[0.], Rot[2]+[0.], [0.,0.,0.,1.] ])
            h = VECTNORM(vect)
            
            def isclose (a,b,filter_threshold=0.5):
                if abs(a-b)<filter_threshold: return True
                else: return False

            if isclose (Mat4f.determinant(Mat4f(*Rot)),
                        0.0, 1E-5):
                return h,Mat4f.scale(1,SIGN(vect[1]),SIGN(vect[2]))
            else: return h,Mat4f(*Rot)
            
        h,rot = vectTransform(vect)
        center = [c/2.0 for c in VECTSUM(pointpair)]
        vect = offset(center,expl)
        batchCylinder.matrix = Mat4f.translate(*vect) *\
            Mat4f.translate(*point) * rot * Mat4f.scale(sx,sx,h)
        batchCylinder.diffuse = MAGENTA
        return batchCylinder

    def cylinders(batches,edgepoints,expl=[1,1,1]):
        
        vects = [VECTDIFF(edge) for edge in edgepoints]
        for pointpair in edgepoints:
            batchCyl = get_cylinder_batch().next()
            batchCyl = transfCylr(batchCyl,pointpair,expl)
            batches += [batchCyl]
        return batches

    def planecells(batches,facepoints,expl=[1,1,1]):
        for points in facepoints:
            n = len(points)
            center = [coord/float(n) for coord in VECTSUM(points)]
            vect = offset(center,expl)
            points = [[point[k]+vect[k] for k in range(3)] for point in points]
            def sign(points):
                return SIGN(VECTPROD(AA(C(VECTDIFF)(center))(points[2:0:-1])))
            face = MKPOL([points,[range(1,n+1)],None])
            faceBatch = Plasm.getBatches(face)
            faceBatch[0].diffuse = WHITE
            batches += faceBatch
        return batches

    def cells(batches,cellpoints,expl=[1,1,1]):
        for points in cellpoints:
            n = len(points)
            center = [coord/float(n) for coord in VECTSUM(points)]
            vect = offset(center,expl)
            points = [[point[k]+vect[k] for k in range(3)] for point in points]
            cell = MKPOL([points,[range(1,n+1)],None])
            cellBatch = Plasm.getBatches(cell)
            cellBatch[0].diffuse = YELLOW
            batches += cellBatch
            # view rotation
            rot = ROTN([ ACOS(INNERPROD([ [1,1,1],[0,0,1] ])), VECTPROD([ [1,1,1],[0,0,1] ]) ])
            batches += Plasm.getBatches(STRUCT([rot, MK([1,1,1])]))
        return batches

    def DRAW0(chain=range(1,g.getNumNode()+1)):

        m = g.getPointDim()
        d = g.getMaxDimCells()
        mapping = [dict(zip(CELLSPERLEVEL(g)(k),range(len(CELLSPERLEVEL(g)(k)))))
                   for k in range(d+1)]

        chains = [[],[],[],[]]
        [chains[g.Level(node)].append(node) for node in chain[::-1]]

        nodepoints = [[g.getVecf(node)[i] for i in range(1,m+1)]
                      if m>2 else
                      [g.getVecf(node)[i] for i in range(1,m+1)]+[0.0]
                      for node in CELLSPERLEVEL(g)(0)]
        

        def translate(pointIds):
            
            return [nodepoints[mapping[0][vert[1]]] for vert in 
                          enumerate(pointIds)]
            
        if m==2: m+=1
        if chains[0]: vertpoints = translate(chains[0])
        if chains[1]:
            edges = [DOWNCELLS(g)(edge) for edge in chains[1]]

            edgepoints = AA(translate)(edges)
            
        if chains[2]:
            facesAsEdges = [DOWNCELLS(g)(face) for face in chains[2]]
            facesAsVerts = [list(set(CAT(AA(DOWNCELLS(g))(face))))
                            for face in facesAsEdges]
            facepoints = AA(translate)(facesAsVerts)
        if d == 3 and chains[3]:
            solidsAsVerts = [UPCELLS(g)(cell) for cell in chains[3]]
            cellpoints = AA(translate)(solidsAsVerts)

        
        batches = []
        if chains[0]:
            batches = spheres(vertpoints,expl)
        if chains[1]:
            batches = cylinders(batches,edgepoints,expl)
        if chains[2]:
            batches = planecells(batches,facepoints,expl)
        if n == 3 and chains[3]:
            batches = cells(batches,cellpoints,expl)

        return batches

    return DRAW0


def PEEK(batches):
    """Like DRAW and VIEW, but more general.

    Display batches.
    """
    if not isinstance(batches,list):
        batches = [batches]
    
    octree = Octree(Batch.Optimize(batches))
    viewer = Viewer(octree)
    viewer.Run()


def print_vertices_coords(g):
    """Print all the vertices coordinates."""

    nav = GraphNavigator()
    vtx = CELLSPERLEVEL(g)(0)
    
    for cell_id in vtx:
        print g.getVecf(cell_id)


if __name__ == '__main__':
    
    hull = SKELETON(1)(SPHERE(1)([8,8]))
    kernel = sphere_kernel()

    #Prima casetta di prova [20,4,16,12]
    batches = graph2batches(kernel)()
    batches += list(Plasm.getBatches(hull))

    PEEK(batches)

    graticcio = exploded_points(kernel)(range(2,28),1.5)
    for elem in graticcio:
        n = kernel.addNode(0); kernel.setVecf(n, Vecf(elem))

    DRAW(kernel)()