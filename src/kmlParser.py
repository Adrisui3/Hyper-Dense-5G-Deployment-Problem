import numpy as np
import fastkml
import shapely
from shapely.ops import triangulate
import matplotlib.pyplot as plt

# KML files are built using Google Earth
# These must contain a polygon representing the area of interest.
# This polygon must contain the number of users inside the area in the description box.
# 

class KMLParser:
    
    # Data related to cells is fixed for now, and it comes from the same paper as the model
    # [id, cost, range, power]
    cells = [[4, 175, 25, 50], [3, 25, 10, 10], [2, 5, 0.5, 1], [1, 1, 0.05, 0.25]]
    
    # Earth radius in kilometers for conversion
    R = 6371
    
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
    
    # For some reason, descriptions come enclosed in <div></div>
    def __extractDescription(self, desc):
        return desc.replace("<div>", "").replace("</div>", "")
    
    def __extractUsers(self, polygon_pm):
        return int(self.__extractDescription(polygon_pm.description))
    
    def __extractCompatibleCells(self, candidate_placemark):
        desc = self.__extractDescription(candidate_placemark.description)
        return list(map(int, desc.split()))
    
    def __distributeUsers(self, polygon, nusers):
        # Areas of interest are abritrary polygons, thus random
        # user locations cannot be generated as usual.
        # An option could be to enclose the polygon inside a rectangle defined by minx, maxx, miny, maxy,
        # and generate random users inside that area, and only keeping those inside the area of interest
        # until the number of required users is met.
        # In order to reduce the number of invalid users, Delunay triangulation can be used to
        # split the area of interest in triangles and use the aforementioned procedure to generate
        # users inside those triangles, granting at most 50% invalid users.




        return None
    
    # Read a KML file and return an initialized Instance object
    def loadKML(self, path, name):
        # KML string loading
        with open(path + name, 'rt', encoding="utf-8") as kml_doc:
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

        cp_coords = [list(point.geometry.coords)[0] for point in candidate_placemarks]
        cp_coords = [(point[0], point[1]) for point in cp_coords]
        
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

        # Uniformly distribute nusers over the area of interest.
        user_locations = self.__distributeUsers(polygon, nusers)








