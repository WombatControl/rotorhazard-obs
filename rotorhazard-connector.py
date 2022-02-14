from importlib.util import source_hash
import json
import obspython as obs
import requests

interval = 5

def refresh_pressed(props, prop):
    """
    Called when the 'refresh' button defined below is pressed
    """
    print("Refresh Pressed")
    update_text()


def update_text():

    source = obs.obs_get_source_by_name(source_name)
    text = "Current Heat: \n" + str(get_current_heat()) + "\n"

    browser = obs.obs_get_source_by_name("Node1")
    
    for pilot in get_pilot_list():
        text += pilot
        text += "\n"

    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", text)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

# ------------------------------------------------------------

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
    """
    Called to define user properties associated with the script. These
    properties are used to define how to show settings properties to a user.
    """
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(props, "source", "Text Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

    """
    TODO: Have list of VLC devices with a common name like VTX5680 that matches with
    each VTX frequency in use. Match devices with pilot frequences to toggle each
    VTX view on and off. (This is going to be tricky.)
    """

    obs.source_list_release(sources)

    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)

    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)

    obs.obs_properties_add_button(props, "button2", "Setup Heats", setup_heats)
    return props


def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    global source_name
    global interval

    print("Update called.")

    obs.timer_remove(update_text)

    source_name = obs.obs_data_get_string(settings, "source")
    interval = obs.obs_data_get_int(settings, "interval")

    if source_name != '':
        obs.timer_add(update_text, interval * 1000)

"""
Add handler for when the scene refreshes - we need to get our pilots and set our nodes properly.
"""

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
        print("Scene has changed...")

        if obs.obs_source_get_name(obs.obs_frontend_get_current_scene()) ==  "RaceView":
            create_race_view()
        else:
            print("Not in RaceView Scene")


def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)


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
    response = requests.get("http://rotorhazard.local/api/heat/all")
    status = json.loads(response.text)

    heats = []
    pilots = []
    heat_list = status["heats"]

    print(heat_list)
