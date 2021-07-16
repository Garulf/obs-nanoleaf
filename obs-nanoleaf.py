import sys
import os

generated_auth_key = None

try:
    import obspython as obs
except ImportError:
    pass

try:
    from nanoleafapi import discovery
except (ImportError, AttributeError):
    script_path = os.path.abspath(os.path.dirname(__file__))
    lib_path = os.path.join(script_path, 'lib')
    print(lib_path)
    sys.path.insert(0, lib_path)
    from nanoleafapi import discovery
    from nanoleafapi import Nanoleaf


def script_description():
    return "This Script will change scenes on your Nanoleaf devices based on if OBS is streaming/recording\n\nFinding devices may freeze OBS for a few moments while your devices are being detected. If you know your devices IP address please enter manually.\n\nPlease hold the power button on your device for 5-7 secs. then press \"Get Authorization Key\"\n\nBy Garulf"


def find_nanoleafs(props, prop):
    nanoleaf_dict = discovery.discover_devices(timeout=10)
    print(nanoleaf_dict)
    l = obs.obs_properties_get(props, "device_ip")
    for device in nanoleaf_dict:
        obs.obs_property_list_add_string(l, nanoleaf_dict[device], nanoleaf_dict[device])

    return True


def authorize_device(props, prop):
    global generated_auth_token
    nl = Nanoleaf(device_ip)
    if nl.generate_auth_token():
        generated_auth_key = nl.auth_token
        s = obs.obs_properties_get(props, "auth_key")
        obs.obs_property_list_add_string(s, generated_auth_key, generated_auth_key)

        return True
    print('[OBS-Nanoleaf]: Unable to acquire Authorization!')
    print('[OBS-Nanoleaf]: Please make sure to Hold the on-off button down for 5-7 seconds until the LED starts flashing in a pattern')


def get_scenes(props, prop):
    if device_ip is not None and auth_key is not None:
        nl = Nanoleaf(device_ip, auth_key)
        s1 = obs.obs_properties_get(props, "scene_on")
        s2 = obs.obs_properties_get(props, "scene_off")
        for light_scene in nl.list_effects():
            obs.obs_property_list_add_string(s1, light_scene, light_scene)
            obs.obs_property_list_add_string(s2, light_scene, light_scene)
        return True


def script_update(settings):
    global device_ip
    global auth_key
    global scene_on
    global scene_off
    global use_last_light_scene

    device_ip = obs.obs_data_get_string(settings, "device_ip")

    use_last_light_scene = obs.obs_data_get_bool(settings, "use_last_light_scene")

    auth_key = obs.obs_data_get_string(settings, "auth_key")

    if device_ip is not None and auth_key is not None:
        scene_on = obs.obs_data_get_string(settings, "scene_on")

        scene_off = obs.obs_data_get_string(settings, "scene_off")



def activated_light_scene():
    global last_light_scene
    nl = Nanoleaf(device_ip, auth_key)
    last_light_scene = nl.get_current_effect()
    nl.set_effect(scene_on)


def deactivate_light_scene():
    global scene_off
    nl = Nanoleaf(device_ip, auth_key)
    if use_last_light_scene:
        scene_off = last_light_scene
    nl.set_effect(scene_off)


def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED or event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        activated_light_scene()
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED or event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        deactivate_light_scene()


def script_load(settings):
    print('rec-nanoleaf script loaded')
    obs.obs_frontend_add_event_callback(on_event)


def script_properties():
    global props
    props = obs.obs_properties_create()
    d = obs.obs_properties_add_list(props, "device_ip", "Device IP:",
                                    obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_properties_add_button(props, "find_nanoleafs", "Find Nanoleafs Devices", find_nanoleafs)
    a = obs.obs_properties_add_list(props, "auth_key", "Authorization Key:", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_properties_add_button(props, "authorize", "Get Authorization Key", authorize_device)
    s1 = obs.obs_properties_add_list(props, "scene_on", "Activate Scene:",
                                     obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    s2 = obs.obs_properties_add_list(props, "scene_off", "Deactivate Scene:",
                                     obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_properties_add_bool(props, "use_last_light_scene", "Use Last Scene")
    obs.obs_properties_add_button(props, "get_scenes", "Get Scenes", get_scenes)
    obs.obs_properties_add_bool(props, "use_last_light_scene", "Use Last Scene")
    return props
