import sys
sys.path.insert(0, './src')
from instance_generator import InstanceGenerator


def generateUniformInstances():
    # UNIFORM INSTANCES #

    # Small instances
    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 50)
    gen.generateInstance(file = "DS1_U")

    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 100)
    gen.generateInstance(file = "DS2_U")

    gen = InstanceGenerator(size = 100, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS3_U")

    # Medium instances
    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS4_U")

    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 200)
    gen.generateInstance(file = "DS5_U")

    gen = InstanceGenerator(size = 200, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS6_U")
    
    # Big instances
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS7_U")
    
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 300)
    gen.generateInstance(file = "DS8_U")



def generateBlobInstances():
    # BLOB INSTANCES #
    
    # Small instances
    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 50)
    gen.generateInstance(file = "DS1_B", blobs = True, cluster_std = 5.0)

    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 100)
    gen.generateInstance(file = "DS2_B", blobs = True, cluster_std = 5.0)

    gen = InstanceGenerator(size = 100, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS3_B", blobs = True, cluster_std = 7.0)

    # Medium instances
    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS4_B", blobs = True, cluster_std =  10.0)

    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 200)
    gen.generateInstance(file = "DS5_B", blobs = True, cluster_std = 10.0)

    gen = InstanceGenerator(size = 200, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS6_B", blobs = True, cluster_std = 10.0)
    
    # Big instances
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS7_B", blobs = True, cluster_std = 15.0)
    
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 300)
    gen.generateInstance(file = "DS8_B", blobs = True, cluster_std = 15.0)



if __name__ == "__main__":    
    
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 300)
    gen.generateInstance(file = "DST_B", blobs = True, cluster_std = 15.0, centers = 5)