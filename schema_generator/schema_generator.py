import logging
from xml.dom import minidom

from utils.golr_utils import parse_config
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

class SchemaGenerator:
    def __init__(self, config, schema_version):
        self.golr_config = parse_config(config)
        self.xml_root = Element('schema')
        self.xml_root.set('name', 'golr')
        self.xml_root.set('version', schema_version)


    def export_schema(self):
         print(self.prettify())

    def prettify(self):
        stringified = self.stringify()
        reparsed = minidom.parseString(stringified)
        return reparsed.toprettyxml(indent="  ")

    def stringify(self):
        return tostring(self.xml_root, 'utf-8')

    def add_element(self, name, properties=None):
        if properties:
            elem = SubElement(self.xml_root, name, **properties)
        else:
            elem = SubElement(self.xml_root, name)
        return elem

    def add_sub_element(self, parent_elem, name, properties=None):
        elem = SubElement(parent_elem, name)
        if properties:
            simple_properties = {}
            for k, v in properties.items():
                print(type(v))
                if isinstance(v, bool):
                    # property value is a bool
                    logging.debug(f"[add_sub_element] property with value as bool: {k} {v}")
                    simple_properties[k] = str(v).lower()
                elif isinstance(v, (str, int, float)):
                    # property value is a primitive type
                    logging.debug(f"[add_sub_element] property with value a primitive type: {k} {v}")
                    simple_properties[k] = v
                elif isinstance(v, list):
                    # property value is a list
                    logging.debug(f"[add_sub_element] property with value as list: {k} {v}")
                    for x in v:
                        self.add_sub_element(elem, k, x)
                elif isinstance(v, dict):
                    # property value is a dict
                    logging.debug(f"[add_sub_element] property with value as dict: {k} {v}")
                    self.add_sub_element(elem, k, v)
                else:
                    logging.error(f"[add_sub_element] unsupported key-value pair: {k} {v}")
                    raise TypeError(f"unsupported key-value pair: {k} {v}")
            self.set_properties(elem, simple_properties)
        return elem

    def set_property(self, elem, key, value):
        elem.set(key, value)

    def set_properties(self, elem, properties):
        for k, v in properties.items():
            elem.set(k, v)

    def write_comment(self, elem, comment):
        c = Comment(comment)
        elem.append(c)
