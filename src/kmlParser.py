import fastkml
import shapely
from shapely.ops import triangulate

# WORK IN PROGRESS

class KMLParser:
    
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