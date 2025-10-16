from lineage_guardian.utils import extract_entities_from_state_block

def test_extract_basic():
txt = "states('binary_sensor.foo_bar') and is_state('person.evert','home')"
ents, macros = extract_entities_from_state_block(txt)
assert 'binary_sensor.foo_bar' in ents
assert 'person.evert' in ents
