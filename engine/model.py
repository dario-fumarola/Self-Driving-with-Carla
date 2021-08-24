
import glob
import os
import sys
import random
import time
import numpy as np
import cv2

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


import carla

IM_WIDTH = 640
IM_HEIGHT = 480
actors = []

def process_img(image):
    i = np.array(image.raw_data)
    #print(i.shape)
    i2 = i.reshape((IM_HEIGHT,IM_WIDTH,4))      # Reshape the data from the sensor in RGBA
    i3 = i2[:, :, :3]                           # We don't care about Alpha in RGBA
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0

try:
    client = carla.Client(host='127.0.0.1', port=2000)                            # Connect to local or remote client
    client.set_timeout(8.0)
    server_version = client.get_server_version()
    client_version = client.get_client_version()
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter("model3")[0]                          # Select Tesla Model 3
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())     # Get a random spawn from the selected map
   
    vehicle = world.spawn_actor(bp, spawn_point)                        # Spawn the blueprint model at spawn
    #vehicle.set_autopilot(True)

    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
    actors.append(vehicle)

    cam_bp = blueprint_library.find("sensor.camera.rgb")                # Get camera
    cam_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
    cam_bp.set_attribute("image_size_y", f"{IM_HEIGHT}")
    cam_bp.set_attribute("fov", "110")

    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))         # Put Camera on top of vehicle

    sensor = world.spawn_actor(cam_bp, spawn_point, attach_to=vehicle)
    actors.append(sensor)
    sensor.listen(lambda data: process_img(data))                       # Get data from sensor


    time.sleep(5)


finally:
    for actor in actors:
        actor.destroy()                                 
        print("Cleaned")
