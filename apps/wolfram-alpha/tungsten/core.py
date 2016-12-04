# -*- coding: utf-8 -*-

"""
tungsten.core
~~~~~~~~~~~~~

Provides user API and response objects
"""

import requests
from xml.etree.ElementTree import fromstring, ElementTree

class Tungsten(object):
    def __init__(self, appid):
        """Create a Tungsten object with a set appid"""
        self.appid = appid

    def query(self, input = '', params = {}):
        """Query Wolfram Alpha and return a Result object"""
        # Get and construct query parameters
        # Default parameters
        payload = {'input': input,
                    'appid': self.appid}
        # Additional parameters (from params), formatted for url
        for key, value in params.items():
            # Check if value is list or tuple type (needs to be comma joined)
            if isinstance(value, (list, tuple)):
                payload[key] = ','.join(value)
            else:
                payload[key] = value

        # Catch any issues with connecting to Wolfram Alpha API
        try:
            r = requests.get("http://api.wolframalpha.com/v2/query", params=payload)

            # Raise Exception (to be returned as error)
            if r.status_code != 200:
                raise Exception('Invalid response status code: %s' % (r.status_code))
            if r.encoding != 'utf-8':
                raise Exception('Invalid encoding: %s' % (r.encoding))

        except Exception, e:
            return Result(error = e)

        return Result(xml = r.text)

class Result(object):
    def __init__(self, xml = '', error = None):
        # ElementTree.fromstring is fragile
        #   Requires byte code, so encode into utf-8
        #   Cannot handle None type, so check if xml exists
        self.xml_tree = None
        if xml:
            self.xml_tree = ElementTree(fromstring(xml.encode('utf-8')))

        # Pass any errors from requesting query along
        self.error_msg = error

    @property
    def success(self):
        # Success from queryresult
        if not self.error_msg:
            return self.xml_tree.getroot().get('success') == 'true'
        else:
            return False

    @property
    def error(self):
        # Check for errors from requesting query
        if self.error_msg:
            return self.error_msg

        # Error from XML group
        error = self.xml_tree.find('error')
        if error is not None:
            return error.find('msg').text
        return None

    @property
    def pods(self):
        """Return list of all Pod objects in result"""
        # Return empty list if xml_tree is not defined (error Result object)
        if not self.xml_tree:
            return []

        # Create a Pod object for every pod group in xml
        return [Pod(elem) for elem in self.xml_tree.findall('pod')]

class Pod(object):
    def __init__(self, pod_root):
        """Create a Pod object using the ElementTree at the root"""
        self.root = pod_root
        self.xml_tree = ElementTree(pod_root)

    @property
    def title(self):
        return self.root.get('title')

    @property
    def id(self):
        return self.root.get('id')

    @property
    def scanner(self):
        return self.root.get('scanner')

    @property
    def format(self):
        """
        Dictionary of available formats, corresponding to a list of the values
        Example: pod.format['plaintext'] will return a list of every plaintext
                 content in the pod's subpods
        """
        formats = {}

        # Iterate through all the tags (formats) in subpods
        # 'state' is a tag but not an acceptable format
        for subpod in self.root.findall('subpod'):

            # elem will be a specific format
            for elem in list(subpod):

                # skip any subpod state xml groups (not a format)
                if elem.tag == 'state':
                    continue

                # Content of elem (specific format)
                content = elem.text

                # img needs special content packaging
                if elem.tag == 'img':
                    content = {'url': elem.get('src'),
                               'alt': elem.get('alt'),
                               'title': elem.get('title'),
                               'width': int(elem.get('width', 0)),
                               'height': int(elem.get('height', 0))}

                # Create / append to return dict
                if elem.tag not in formats:
                    formats[elem.tag] = [content]
                else:
                    formats[elem.tag].append(content)

        return formats

