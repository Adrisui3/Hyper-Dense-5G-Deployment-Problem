import numpy as np
import math
import random
from os.path import exists as file_exists
import fastkml
import shapely
from shapely.ops import triangulate

'''
    KML files are built using Google Earth.
    Each file must contain a polygon representing the area of interest.
    All candidate locations, represented by placemarks, must be inside
    the polygon.
'''

class KMLParser:    
    # Earth radius in kilometers for conversion
    R = 6371
    
    def __init__(self, cells_file = "data/cells_default.txt"):
        self.cells = self.__loadCells(file = cells_file)

    def __loadCells(self, file):        
        cells = []
        with open(file = file) as f:
            ds = f.readlines()
            for line in range(len(ds)):
                cdata = ds[line].split()
                cells.append([int(cdata[0]), float(cdata[1]), float(cdata[2]), float(cdata[3])])

        return cells
    
    def __distance(self, p1, p2):
        lon1 = np.radians(p1[0])
        lon2 = np.radians(p2[0])
        lat1 = np.radians(p1[1])
        lat2 = np.radians(p2[1])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    
        c = 2 * np.arcsin(np.sqrt(a))

        return c * self.R
        
        #return np.sqrt(pow(p1[0] - p2[0], 2) + pow(p2[1] - p1[1], 2))
    
    def __mercatorProjection(self, point):
        x = math.radians(point[0]) * self.R
        y = math.log(math.tan(math.pi / 4 + math.radians(point[1]) / 2)) * self.R
        return (x, y)
    
    # For some reason, descriptions come enclosed in <div></div>
    def __extractDescription(self, desc):
        return desc.replace("<div>", "").replace("</div>", "")
    
    def __extractUsers(self, polygon_pm):
        return int(self.__extractDescription(polygon_pm.description))
    
    def __extractCompatibleCells(self, candidate_placemark):
        desc = self.__extractDescription(candidate_placemark.description)
        return list(map(int, desc.split()))
    
    def __distributeUsers(self, polygon, nusers):
        ''' 
            Uniformly distributes users inside the polygon.
            
            In order to prevent discarding too many users that
            may be generated outside the polygon, it performs Delaunay
            triangulation on it and then generates users inside a bounding
            box for each triangle. This ensures that the number of discarded
            users is minimum.
        '''

        user_locations = []
        p_area = polygon.area
        triangles = triangulate(polygon)
        for t in triangles:
            minx, miny, maxx, maxy = t.bounds
            bbox = shapely.geometry.box(minx, miny, maxx, maxy)

            nusersTriangle = math.ceil((t.area / p_area) * nusers)
            nusersInside = 0
            while nusersInside < nusersTriangle:
                user = shapely.geometry.Point((random.uniform(minx, maxx), random.uniform(miny, maxy)))
                if polygon.contains(user):
                    user_locations.append((user.x, user.y))
                    nusersInside += 1

        while len(user_locations) - nusers > 0:
            user_locations.pop()

        return user_locations
    
    # Read a KML file and return its content in a dictionary used to initialize an Instance object
    def loadKML(self, path, file):
        # KML string loading
        with open(path + file, 'rt', encoding="utf-8") as kml_doc:
            ds_string = kml_doc.read().encode()
        
        ds = fastkml.kml.KML()
        ds.from_string(ds_string)
        
        # Apparently this is the way to extract features...?
        ds_features = list(list(ds.features())[0].features())
        
        polygon = None
        candidate_placemarks = []

        for pm in ds_features:
            if pm.name == "P":
                polygon = pm
            elif pm.name == "CP":
                candidate_placemarks.append(pm)
            else:
                print("ERROR: non-recognized placemark ", pm.name)
                exit()

        
        # Verify if any placemark is not placed inside the polygon
        for c_pm in candidate_placemarks:
            if not polygon.geometry.contains(c_pm.geometry):
                print("ERROR: ", c_pm.geometry, " placemark is outside the area of interest!")
                exit()

        # All coordinates are represented in longitude, latitude and altitude.
        # Altitude will not be taken into account to simplify the model
        polygon_bounds = list(polygon.geometry.exterior.coords)
        polygon_bounds = [(point[0], point[1]) for point in polygon_bounds]
        #polygon_bounds = [self.__mercatorProjection((point[0], point[1])) for point in polygon_bounds]

        cp_coords = [list(point.geometry.coords)[0] for point in candidate_placemarks]
        cp_coords = [(point[0], point[1]) for point in cp_coords]
        #cp_coords = [self.__mercatorProjection((point[0], point[1])) for point in cp_coords]

        # Rebuild geometries without altitude
        polygon.geometry = shapely.geometry.Polygon(polygon_bounds)
        for i in range(len(candidate_placemarks)):
            candidate_placemarks[i].geometry = shapely.geometry.Point(cp_coords[i])
        
        # Extract number of users from AoI description
        nusers = self.__extractUsers(polygon)
        
        # For every candidate placemark, extract compatible cell kinds from description box
        # and build compatibility dictionary
        cell_compatibility = {cell[0]:set() for cell in self.cells}
        for i in range(len(candidate_placemarks)):
            c_cells = self.__extractCompatibleCells(candidate_placemarks[i])
            for cell in c_cells:
                cell_compatibility[cell].add(i)
        
        # Extract candidate location coordinates from placemarks
        candidate_locations = []
        for pm in candidate_placemarks:
            candidate_locations.append(list(pm.geometry.coords)[0])
        
        ncandidates = len(candidate_locations)

        # To guarantee that all tests are run using the same datasets,
        # corresponding users for each KML instance will be stored in a different file.
        user_locations = []
        ufile = file.replace(".kml", ".usr")
        if file_exists(path + "users/" + ufile):
            with open(path + "users/" + ufile, "r") as f:
                uds = f.readlines()
                line = 1
                for _ in range(nusers):
                    uloc = list(map(float, uds[line].split()))
                    user_locations.append(tuple(uloc))
                    line += 1
        else:
            user_locations = self.__distributeUsers(polygon.geometry, nusers)
            with open(path + "users/" + ufile, "w") as f:
                print("# User coordinates for KML file", file = f)
                for u in user_locations:
                    print(u[0], u[1], file = f)


        # Compute distance matrices
        dmatrix_users_candidates = [[] for _ in range(nusers)]
        dmatrix_candidates = [[] for _ in range(ncandidates)]
        for i in range(nusers):
            for j in range(ncandidates):
                dist = self.__distance(user_locations[i], candidate_locations[j])
                dmatrix_users_candidates[i].append(dist)

        for i in range(ncandidates):
            for j in range(ncandidates):
                dist = 0 if i == j else self.__distance(candidate_locations[i], candidate_locations[j])
                dmatrix_candidates[i].append(dist)
        
        cells = {cell[0]:cell[1:] for cell in self.cells}
        cells_ids = cells.keys()
        macro_id = max(cells_ids)

        init_deployment = [0 for _ in range(ncandidates)]
        return {"polygon":polygon.geometry, "cells":cells, "cells_ids":cells_ids, "macro_id":macro_id,
                "init_deployment":init_deployment, "cell_compatibility":cell_compatibility,
                "nusers":nusers, "ncandidates":ncandidates, "dmatrix_users_candidates":dmatrix_users_candidates,
                "dmatrix_candidates":dmatrix_candidates, "user_locations":user_locations, 
                "candidate_locations":candidate_locations}