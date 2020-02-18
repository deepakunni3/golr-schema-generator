import os
from golr_schema_generator.golr_schema_generator import GolrSchemaGenerator

cwd = os.path.abspath(os.path.dirname(__file__))
resource_dir = os.path.join(cwd, 'resources')
target_dir = os.path.join(cwd, 'target')


def test_simple_config():
    config = os.path.join(resource_dir, 'simple-config.yaml')
    schema_output = os.path.join(target_dir, 'simple-config-schema.xml')
    generator = GolrSchemaGenerator(config)
    generator.generate_schema()
    generator.export_schema(schema_output)
    it = generator.xml_root.iter()
    elements = [x for x in it]
    assert len(elements) == 37
    children = list(generator.xml_root)
    assert len(children) == 3
    fields = children[1]
    assert len(list(fields)) == 11


def test_oban_config():
    config = os.path.join(resource_dir, 'oban-config.yaml')
    schema_output = os.path.join(target_dir, 'oban-config-schema.xml')
    generator = GolrSchemaGenerator(config)
    generator.generate_schema()
    generator.export_schema(schema_output)
    it = generator.xml_root.iter()
    elements = [x for x in it]
    assert len(elements) == 304
    children = list(generator.xml_root)
    assert len(children) == 3
    fields = children[1]
    assert len(list(fields)) == 278


def test_ont_config():
    config = os.path.join(resource_dir, 'ont-config.yaml')
    schema_output = os.path.join(target_dir, 'ont-config-schema.xml')
    generator = GolrSchemaGenerator(config)
    generator.generate_schema()
    generator.export_schema(schema_output)
    it = generator.xml_root.iter()
    elements = [x for x in it]
    assert len(elements) == 114
    children = list(generator.xml_root)
    assert len(children) == 3
    fields = children[1]
    assert len(list(fields)) == 88