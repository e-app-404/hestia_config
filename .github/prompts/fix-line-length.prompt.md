---
description: "Fix all 'line too long' linter errors in a file while preserving functionality"
mode: "edit"
model: "GPT-4o"
tools: ["readFile", "editFile"]
---

# Fix Line Length Violations

Analyze the provided file and fix all "line too long" linter errors while maintaining code functionality, readability, and style consistency.

## Target File

Use the currently selected file: `${file}`

If no file is selected, ask the user to specify the file path.

## Requirements

### Line Length Standards
- **Python**: Maximum 88 characters (Black formatter standard) or 79 characters (PEP 8)
- **JavaScript/TypeScript**: Maximum 80-100 characters (project-specific)
- **YAML**: Maximum 80 characters for readability
- **Markdown**: Maximum 80 characters for prose, unlimited for code blocks
- **Shell scripts**: Maximum 80 characters

### Fixing Strategies

Apply these techniques in order of preference:

1. **Break long expressions**:
   ```python
   # Before
   result = some_very_long_function_name(argument1, argument2, argument3, argument4)
   
   # After
   result = some_very_long_function_name(
       argument1, argument2, argument3, argument4
   )
   ```

2. **Split string literals**:
   ```python
   # Before
   message = "This is a very long error message that exceeds the line length limit"
   
   # After
   message = (
       "This is a very long error message "
       "that exceeds the line length limit"
   )
   ```

3. **Break method chains**:
   ```python
   # Before
   data = df.filter(col("status") == "active").select("id", "name").orderBy("name")
   
   # After
   data = (
       df.filter(col("status") == "active")
       .select("id", "name")
       .orderBy("name")
   )
   ```

4. **Extract variables for complex expressions**:
   ```python
   # Before
   if user.has_permission("read") and user.is_active and user.department == "engineering":
   
   # After
   has_read_access = user.has_permission("read")
   is_active_engineer = user.is_active and user.department == "engineering"
   if has_read_access and is_active_engineer:
   ```

5. **Use trailing commas for multi-line collections**:
   ```python
   # Before
   items = ["item1", "item2", "item3", "item4", "item5"]
   
   # After
   items = [
       "item1",
       "item2", 
       "item3",
       "item4",
       "item5",
   ]
   ```

### Language-Specific Guidelines

**Python**:
- Use parentheses for implicit line continuation
- Follow PEP 8 indentation (4 spaces for continuation)
- Use Black-style formatting when possible

**YAML**:
- Use YAML folded scalars (`>`) for long text
- Break long lists into multiple lines
- Maintain proper indentation (2 spaces)

**JavaScript/TypeScript**:
- Use template literals for long strings
- Break object properties and array elements
- Consider destructuring for long parameter lists

**Shell Scripts**:
- Use backslash continuation (`\`)
- Break long command pipelines
- Use here-docs for long strings

### Preservation Requirements

- **Maintain functionality**: No behavioral changes
- **Preserve comments**: Keep all existing comments intact
- **Maintain formatting style**: Follow existing code style patterns
- **Keep semantics**: No changes to logic or data structures
- **Preserve imports**: Don't modify import statements unless absolutely necessary

## Output Format

1. **Summary**: Brief description of changes made
2. **Modified file**: Complete file content with all line length issues resolved
3. **Change log**: List of specific line numbers and modifications made

## Validation

Before completing:
- Verify no lines exceed the target length limit
- Confirm all syntax is valid
- Ensure code functionality is preserved
- Check that formatting follows project conventions

## Example Usage

Input variables:
- `${file}`: Path to the file to fix
- `${selection}`: Selected code (if any) to focus on specific sections

Run this prompt on files with linter errors like:
- `E501 line too long (95 > 88 characters)`
- `line-length: Line is too long (120/80)`
- `max-len: Line exceeds maximum length`