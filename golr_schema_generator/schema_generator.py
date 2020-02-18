import logging
from xml.dom import minidom

from golr_schema_generator.utils.golr_utils import parse_config
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

class SchemaGenerator:
    """
    Base class for implementing a SchemaGenerator that outputs XML
    from a given YAML configuration.

    Parameters
    ----------
    config: str
        A YAML config filename with GOlr fields and their descriptions

    """
    def __init__(self, config: str):
        self.golr_config = parse_config(config)
        self.xml_root = Element('schema')
        self.xml_root.set('name', 'golr')

    def add_element(self, name: str, properties: dict = None) -> Element:
        """
        Add an element to the root of the XML.

        Parameters
        ----------
        name: str
            The name of the element to be added to root
        properties: dict
            A dictionary with properties for the element

        Returns
        -------
        xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance of the added element

        """
        if properties:
            elem = SubElement(self.xml_root, name, **properties)
        else:
            elem = SubElement(self.xml_root, name)
        return elem

    def add_sub_element(self, parent_elem: Element, name: str, properties: dict = None) -> Element:
        """
        Add a sub element with ``name`` to ``parent_elem``, along with properties.

        Parameters
        ----------
        parent_elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance of the parent element
        name: str
            The name of the element to be added as sub element
        properties: dict
            A dictionary with properties for the element

        Returns
        -------
        xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance of the added element

        """
        elem = SubElement(parent_elem, name)
        if properties:
            simple_properties = {}
            for k, v in properties.items():
                if isinstance(v, bool):
                    # property value is a bool
                    logging.debug(f"property with value as bool: {k} {v}")
                    simple_properties[k] = str(v).lower()
                elif isinstance(v, (str, int, float)):
                    # property value is a primitive type
                    logging.debug(f"property with value a primitive type: {k} {v}")
                    simple_properties[k] = v
                elif isinstance(v, list):
                    # property value is a list
                    logging.debug(f"property with value as list: {k} {v}")
                    for x in v:
                        self.add_sub_element(elem, k, x)
                elif isinstance(v, dict):
                    # property value is a dict
                    logging.debug(f"property with value as dict: {k} {v}")
                    self.add_sub_element(elem, k, v)
                else:
                    logging.error(f"unsupported key-value pair: {k} {v}")
                    raise TypeError(f"unsupported key-value pair: {k} {v}")
            self.set_properties(elem, simple_properties)
        return elem

    def set_property(self, elem: Element, key: str, value: str) -> None:
        """
        Set property of an element.

        Parameters
        ----------
        elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance
        key: str
            The key of property
        value: str
            The value of property

        """
        elem.set(key, value)

    def set_properties(self, elem: Element, properties: dict) -> None:
        """
        Set properties of an element.

        Parameters
        ----------
        elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance
        properties: dict
            A dictionary that has one or more properties

        """
        for k, v in properties.items():
            elem.set(k, v)

    def write_comment(self, elem: Element, comment: str) -> None:
        """
        Write comments in the scope of a given element.

        Parameters
        ----------
        elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance
        comment: str
            The comment as string

        """
        c = Comment(comment)
        elem.append(c)

    def export_schema(self, filename: str = None) -> None:
        """
        Export the XML schema.

        Parameters
        ----------
        filename: str
            A filename to write the XML

        """
        if filename:
            WH = open(filename, 'w')
            WH.write(self.prettify())
        else:
            print(self.prettify())

    def prettify(self, indent: str = "  ") -> str:
        """
        Prettify the XML schema.

        Parameters
        ----------
        indent: str
            The indentation to use in the XML (default: ``"  "``)

        Returns
        -------
        str
            A pretty, indented, serialized representation

        """
        stringified = self.stringify()
        reparsed = minidom.parseString(stringified)
        return reparsed.toprettyxml(indent)

    def stringify(self) -> str:
        """
        Serialize XML as a string.

        Returns
        -------
        str
            The serialized representation

        """
        return tostring(self.xml_root, 'utf-8')

