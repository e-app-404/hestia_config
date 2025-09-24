
#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def normalize_to_tojson_block(key, values, indent):
    value_list = [v.strip().strip('"') for v in values.split(',')]
    json_array = ', '.join(f'"{v}"' for v in value_list)
    return f"{indent}{key}: >\n{indent}  {{{{ [{json_array}] | tojson }}}}"

def transform_yaml_attributes_block(yaml_text):
    lines = yaml_text.splitlines()
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        output.append(line)
        if re.match(r'\s*(attribute_templates|attributes):\s*', line):
            i += 1
            while i < len(lines) and re.match(r'^\s+\w+:', lines[i]):
                current_line = lines[i]
                indent_match = re.match(r'^(\s+)(\w+):\s*(.*)', current_line)
                if not indent_match:
                    output.append(current_line)
                    i += 1
                    continue
                indent, key, value = indent_match.groups()

                if re.match(r'^".*?"(?:,\s*".*?")+$', value):
                    output.append(normalize_to_tojson_block(key, value.replace('"', ''), indent))
                elif re.match(r'^".*?,.*?"$', value):
                    output.append(normalize_to_tojson_block(key, value.strip('"'), indent))
                elif re.match(r'^[^",]+(?:,\s*[^",]+)+$', value):
                    output.append(normalize_to_tojson_block(key, value, indent))
                elif value == '':
                    list_lines = []
                    j = i + 1
                    while j < len(lines) and re.match(r'^\s+-\s*\w+', lines[j]):
                        match_item = re.search(r'-\s*(\w+)', lines[j])
                        if match_item:
                            list_lines.append(match_item.group(1))
                        j += 1
                    if list_lines:
                        json_array = ', '.join(f'"{item}"' for item in list_lines)
                        output.append(f"{indent}{key}: >\n{indent}  {{ {{ [{json_array}] | tojson }} }}")
                        i = j - 1
                    else:
                        output.append(current_line)
                elif re.match(r'^\[.*?\]$', value):
                    cleaned = value.strip('[]')
                    output.append(normalize_to_tojson_block(key, cleaned, indent))
                elif value.strip() == '>':
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('{{') and 'tojson' not in next_line:
                            value_inside = re.search(r'\[\s*(.*?)\s*\]', next_line)
                            if value_inside:
                                items = value_inside.group(1)
                                output.append(f"{indent}{key}: >\n{indent}  {{ {{ [{items}] | tojson }} }}")
                                i += 1
                            else:
                                output.append(current_line)
                        else:
                            output.append(current_line)
                    else:
                        output.append(current_line)
                else:
                    output.append(current_line)
                i += 1
        else:
            i += 1
    return '\n'.join(output)

if __name__ == "__main__":
    file_path = Path(sys.argv[1])
    with file_path.open() as f:
        input_text = f.read()

    updated = transform_yaml_attributes_block(input_text)
    file_path.write_text(updated)
    print(f"Transformed: {file_path}")
