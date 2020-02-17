import re
import logging
from xml.etree.ElementTree import Element

from schema_generator.schema_generator import SchemaGenerator


# TODO: move to JSON
# TODO: add JSON schema to validate the structure of this JSON
FIELD_TYPES = {
    'string': {
        'name': 'string',
        'class': 'solr.StrField',
        'sortMissingLast': 'true'
    },
    'text_searchable': {
        'name': 'text_searchable',
        'class': 'solr.TextField',
        'positionIncrementGap': '100',
        'sortMissingLast': 'true',
        'analyzer': [
            {
                'type': 'index',
                'charFilter': {
                    'class': 'solr.PatternReplaceCharFilterFactory',
                    'pattern': '_',
                    'replacement': ' '
                },
                'tokenizer': {
                    'class': 'solr.StandardTokenizerFactory'
                },
                'filter': [
                    {
                        'class': 'solr.LowerCaseFilterFactory'
                    },
                    {
                        'class': 'solr.EdgeNGramFilterFactory',
                        'minGramSize': '3',
                        'maxGramSize': '50'
                    }
                ]
            },
            {
                'type': 'query',
                'charFilter': {
                    'class': 'solr.PatternReplaceCharFilterFactory',
                    'pattern': '_',
                    'replacement': ' '
                },
                'tokenizer': {
                    'class': 'solr.StandardTokenizerFactory'
                },
                'filter': [
                    {
                        'class': 'solr.LowerCaseFilterFactory'
                    }
                ]
            }
        ]
    },
    'integer': {
        'name': 'integer',
        'class': 'solr.TrieIntField',
        'precisionStep': '0',
        'positionIncrementGap': '0',
        'sortMissingLast': 'true'
    },
    'boolean': {
        'name': 'boolean',
        'class': 'solr.BoolField',
        'sortMissingLast': 'true'
    },
    'booleans': {
        'name': 'booleans',
        'class': 'solr.BoolField',
        'sortMissingLast': 'true',
        'multiValued': 'true'
    },
    'long': {
        'name': 'long',
        'class': 'solr.TrieLongField'
    },
    'tdates': {
        'name': 'tdates',
        'class': 'solr.TrieDateField',
        'positionIncrementGap': '0',
        'docValues': 'true',
        'multiValued': 'true',
        'precisionStep': '6'
    },
    'tlongs': {
        'name': 'tlongs',
        'class': 'solr.TrieLongField',
        'positionIncrementGap': '0',
        'docValues': 'true',
        'multiValued': 'true',
        'precisionStep': '8'
    },
    'tdoubles': {
        'name': 'tdoubles',
        'class': 'solr.TrieDoubleField',
        'positionIncrementGap': '0',
        'docValues': 'true',
        'multiValued': 'true',
        'precisionStep': '8'
    }
}


class GolrSchemaGenerator(SchemaGenerator):
    """
    Class for generating a GOlr Schema XML from a given YAML configuration.

    Parameters
    ----------
    config: dict
        A YAML config with GOlr fields and their descriptions
    schema_version: float
        The version of Solr for which this schema is being built (default: ``6.2``)

    """
    closure_label_regex = re.compile('(.*)_closure_label$')
    list_label_regex = re.compile('(.*)_list_label$')

    def __init__(self, config, schema_version='6.2'):
        super(GolrSchemaGenerator, self).__init__(config)
        self.xml_root.set('version', schema_version)

    def generate_automatic_fields(self, parent_elem: Element, golr_field: dict) -> None:
        """
        Automatically add fields to the schema based on properties of a ``golr_field``.

        Parameters
        ----------
        parent_elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance of the parent element
        golr_field: dict
            A dictionary containing properties that defines a golr_field

        """
        closure_label_regex_match = self.closure_label_regex.match(golr_field['id'])
        list_label_regex_match = self.list_label_regex.match(golr_field['id'])

        basename = None
        suffix = None
        if closure_label_regex_match:
            basename = closure_label_regex_match.groups[0]
            suffix = "_closure_map"
        if list_label_regex_match:
            basename = list_label_regex_match.groups[0]
            suffix = "_list_map"

        if suffix:
            self.write_comment(parent_elem, f"Automatically created to capture mapping information between {basename}_(list|closure) and {golr_field['id']}")
            self.write_comment(parent_elem, f"It is not indexed for searching (JSON blob), but may be useful to the client.")

        self.add_sub_element(parent_elem, "field", {
            'name': f'{basename}{suffix}',
            'type': 'string',
            'required': False,
            'multiValued': False,
            'indexed': False,
            'stored': True
        })

    def generate_all_fields(self, parent_elem: Element) -> None:
        """
        Generate all the fields as defined by the YAML configuration.

        Parameters
        ----------
        parent_elem: xml.etree.ElementTree.Element
            ``xml.etree.ElementTree.Element`` instance of the parent element

        """
        for golr_field in self.golr_config['fields']:
            # TODO: support comments in YAML
            # any comments in the config YAML will be dropped.
            # If comments are a priority then they should be made into a golr_field property.
            field_id = golr_field['id']
            field_type = golr_field['type']
            field_required = golr_field['required'] if 'required' in golr_field else False
            field_multi = True
            field_indexed = golr_field['indexed'] if 'indexed' in golr_field else False
            field_searchable = golr_field['searchable'] if 'searchable' in golr_field else False
            field_cardinality = golr_field['cardinality'] if 'cardinality' in golr_field else 'single'

            if field_id == 'id':
                golr_field['required'] = True

            if field_cardinality == 'single':
                field_multi = False

            self.add_sub_element(parent_elem, 'field', {
                'name': field_id,
                'type': field_type,
                'required': field_required,
                'multiValued': field_multi,
                'indexed': field_indexed,
                'stored': True
            })

            if field_searchable:
                searchable_field_id = f'{field_id}_searchable'
                self.write_comment(parent_elem, f'An easily searchable (TextField tokenized) version of {field_id}.')
                self.add_sub_element(parent_elem, 'field', {
                    'name': searchable_field_id,
                    'type': 'text_searchable',
                    'required': field_required,
                    'multiValued': field_multi,
                    'indexed': True,
                    'stored': True
                })

                self.add_sub_element(parent_elem, 'copyField', {
                    'source': field_id,
                    'dest': searchable_field_id
                })

    def generate_schema(self) -> None:
        """
        Generate the XML schema from GOlr YAML configuration.

        """
        types_elem = self.add_element('types')
        self.write_comment(types_elem, 'Unsplit string for when text needs to be dealt with atomically.')
        self.write_comment(types_elem, 'For example, faceted querying.')

        fields_elem = self.add_element('fields')
        self.write_comment(fields_elem, 'A special static/fixed (by YAML conf file) field all documents have.')
        for field_type in FIELD_TYPES:
            self.add_sub_element(types_elem, 'fieldType', FIELD_TYPES[field_type])

        self.add_sub_element(fields_elem, 'field', {
            'name': 'document_category',
            'type': 'string',
            'required': False,
            'multiValued': False,
            'indexed': True,
            'stored': True
        })

        self.write_comment(fields_elem, 'Required by Solr.')
        self.add_sub_element(fields_elem, 'field', {
            'name': '_version_',
            'type': 'long',
            'multiValued': False,
            'indexed': True,
            'stored': True
        })

        self.generate_all_fields(fields_elem)

        unique_key_elem = self.add_element('uniqueKey')
        unique_key_elem.text = 'id'
