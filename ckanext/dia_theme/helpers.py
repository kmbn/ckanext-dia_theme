from ckan.common import config, request
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import url_for
import json


def parent_site_url():
    """
    Return the URL of the parent site (eg, if this instance
    is running in a CKAN + CMS config). Returns the setting
    ckan.parent_site_url, or value of h.url('home') if that
    setting is missing
    """
    return config.get('ckan.parent_site_url', toolkit.h.url('home'))


def modify_geojson(geojson_string):
    """
    Returns 'fixed' geojson if the input is a Polygon or MultiPolygon type.
    Valid geojson should be within the -180, 180 range, but for most datasets this will render a very zoomed out view of
    the map. Instead, we map latitudes under 0th meridian to be +360, which makes the map look a lot nicer for most
    polygons that span the 180th meridian.

    :param geojson_string:
    :return:
    """
    obj = json.loads(geojson_string)

    if isinstance(obj, dict):
        new_coords = []
        if obj.get('type', None) == 'Polygon':
            for shape in obj.get('coordinates'):
                new_coords.append([_modify(c) for c in shape])
        elif obj.get('type', None) == 'MultiPolygon':
            for shape in obj.get('coordinates'):
                new_coords.append([[_modify(c) for c in shape[0]]])
        else:
            return geojson_string

        obj['coordinates'] = new_coords
        return json.dumps(obj)
    else:
        return geojson_string


def _modify(coord):
    lat, long = coord
    if lat < 0:
        lat = lat + 360
    return [lat, long]


def make_nav_links():
    current_url = request.environ['CKAN_CURRENT_URL']
    if current_url[0] != "/":
        current_url = "/{}".format(current_url)
    pages = [
        ("package", "search", "Search for datasets", "Datasets"),
        ("organization", "index", "Go to the organizations page", "Organizations"),
        ("group", "index", "Go to the groups page", "Groups"),
        ("home.about", None, "Go to the about page", "About"),
        ("user.login", None, "Go to the log in page", "Log in"),
        ("user.register", None, "Go to the registration page", "Register"),
    ]
    links = []
    for controller, action, title, text in pages:
        url = url_for(controller, action).replace("package", "dataset")
        if url[0] != "/":
            url = "/{}".format(url)
        if url == current_url:
            _class = "site-header__menu-item menu-item current"
        else:
            _class = "site-header__menu-item menu-item"
        links.append(
            (url, _class, title, text)
            )
    return links
