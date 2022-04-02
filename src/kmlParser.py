import numpy as np
import fastkml
import shapely
from shapely.ops import triangulate
import matplotlib.pyplot as plt

# WORK IN PROGRESS

class KMLParser:
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
                polygon = pm.geometry
            else:
                candidate_placemarks.append(pm)
        
        # Verify if any placemark is not placed inside the polygon
        for c_pm in candidate_placemarks:
            if not polygon.contains(c_pm.geometry):
                print("ERROR: ", c_pm.geometry, " placemark is outside the area of interest!")

        # All coordinates are represented in longitude, latitude and altitude.
        # Altitude will not be taken into account to simplify the model
        bounds = list(polygon.exterior.coords)
        cp_coords = [list(point.geometry.coords)[0] for point in candidate_placemarks]
        
        bounds = [(point[0], point[1]) for point in bounds]
        cp_coords = [(point[0], point[1]) for point in cp_coords]

        '''
        for point in bounds:
            plt.plot(point[0], point[1], marker='o', markersize=20, color='red')
        
        for point in cp_coords:
            plt.plot(point[0], point[1], marker='x', markersize=10, color = 'blue')
        
        plt.show()
        '''