from importlib.util import source_hash
import json
import obspython as obs
import requests


def refresh_pressed(props, prop):
    pass

def get_current_heat():
    response = requests.get("http://rotorhazard.local/api/status")
    status = json.loads(response.text)

    return status['status']['state']['current_heat']


def get_pilot_list():
    response = requests.get("http://rotorhazard.local/api/race/current")
    status = json.loads(response.text)

    pilots = []
    pilot_list = status["race"]["leaderboard"]["by_race_time"]

    for pilot in pilot_list:
        pilots.append(pilot["callsign"])

    return pilots

def get_nodes_list():
    response = requests.get("http://rotorhazard.local/api/race/current")
    status = json.loads(response.text)

    nodes = []
    nodes_list = status["race"]["leaderboard"]["by_race_time"]

    """Note: We need to increment by 1 here because the API is zero-incremented, but the node display is not."""
    for node in nodes_list:
        nodes.append(node["node"] + 1) 

    return nodes

def script_properties():
    props = obs.obs_properties_create()

    return props


def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """

    print("Script Updated.")



def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:

        # TODO - Have the scene be changeable through a configuration item.
        if obs.obs_source_get_name(obs.obs_frontend_get_current_scene()) ==  "RaceView":
            update_race_view()
        else:
            print("Not in RaceView Scene")

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def update_race_view():
        
    hide_video_sources()

    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)
    nodes = get_populated_nodes()
    sources = obs.obs_enum_sources()

    for view, (node, pilot) in enumerate(nodes.items(), 1):
        for source in sources:
            if obs.obs_source_get_name(source) == "Pilot" + str(view):
                update_obs_view(str(node), source)
                attach_video(str(view), str(node))

def hide_video_sources():

    # We want to toggle off any video sources and reenable them one-by-one so we don't get a mess of video sources when we switch heats.
    # Start by querying the number of nodes in our Rotorhazard system
    response = requests.get("http://rotorhazard.local/api/status")
    status = json.loads(response.text)

    num_nodes = status['status']['state']['num_nodes']

    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)

    # Now we iterate through each potential 'VRX #' source in OBS and turn them off one by one if they exist. We will turn them back on when we call
    # the attach_video function.
    for i in range(1, num_nodes):
        video_display = obs.obs_scene_find_source(scene, "VRX" + str(i))
        if video_display:
            obs.obs_sceneitem_set_visible(video_display, False)

    obs.obs_scene_release(scene)

def attach_video(view, node):
    # We want to find the source for the VRX object for each RH node. There should be one VTX source for each node in use on the RH server.
    # There are limits to how many USB-OTG receivers can be used, so we are not checking to see what kind of source we are using to allow for VLC streams, etc.
    # Right now each VRX has to be named in the format "VRX#"
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)

    node_display = obs.obs_scene_find_source(scene, "Pilot" + view)
    video_display = obs.obs_scene_find_source(scene, "VRX" + node)

    if video_display and node_display:
        # Get the (x,y) coordinates for the source with the RotorHazard streaming display and set the video display to those coordinates.
        pos = obs.vec2()
        obs.obs_sceneitem_get_pos(node_display, pos)
        obs.obs_sceneitem_set_pos(video_display, pos)
        
        # Unhide the video display.
        obs.obs_sceneitem_set_visible(video_display, True)

    obs.obs_scene_release(scene)


def create_race_view():
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)
    nodes = get_nodes_list()
    settings = obs.obs_data_create()

    obs.obs_data_set_string(
        settings, "url", "http://rotorhazard.local/stream/node/1"
    )
        
    source = obs.obs_source_create_private("browser_source", "test_py", settings)
    obs.obs_scene_add(scene, source)
        
    obs.obs_scene_release(scene)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)

    # Step one - go through each node and see if a OBS view has been created for it.
    """for node in nodes:
        nodeFound = 0
        node_string = str(node)
        sources = obs.obs_enum_sources()

        for source in sources:
            if obs.obs_source_get_name(source) == "rh_node" + node_string:
                update_obs_view(node_string, source)
                nodeFound = 1
        
        if nodeFound == 0:
            settings = obs.obs_data_create()
            print("We did not find rh_node" + node_string + " so we need to create it.")
            obs.obs_data_set_string(settings, "url", "http://rotorhazard.local/stream/node/" + node_string)
            new_source = obs.obs_source_create("browser_source", "rh_node" + node_string, settings, None)
            obs.obs_scene_add(scene, new_source)
            obs.obs_data_release(settings)
            obs.obs_source_release(new_source)

        obs.source_list_release(sources)

    obs.obs_scene_release(scene)
    """

def update_obs_view(node, source):

    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "url", "http://rotorhazard.local/stream/node/" + node)
    obs.obs_source_update(source, settings)
    obs.obs_source_release(source)
    obs.obs_data_release(settings)
    
def setup_heats(props, prop):
    pass

def get_populated_nodes():
    current_heat = get_current_heat()

    response = requests.get("http://rotorhazard.local/api/heat/" + str(current_heat))
    status = json.loads(response.text)

    nodes_list = status["heat"]["setup"]["nodes_pilots"]

    populated_nodes = {}

    for node, pilot in nodes_list.items():
        #print("Node: " + node)
        #print("Pilot: " + str(pilot))

        if pilot == 0:
            pass
        else:
            populated_nodes.update({int(node) + 1: pilot})

    return(populated_nodes)