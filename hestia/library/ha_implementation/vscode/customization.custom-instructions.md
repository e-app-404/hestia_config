---
title: "Use custom instructions in VS Code"
authors: "Microsoft VS Code Team"
source: "VS Code Documentation"
slug: "vscode-custom-instructions"
tags: ["vscode", "copilot", "ai", "customization", "instructions"]
original_date: "2021-03-11"
last_updated: "2025-10-15"
url: "https://code.visualstudio.com/docs/copilot/customization/custom-instructions"
---

# Use custom instructions in VS Code

Custom instructions enable you to define common guidelines and rules that automatically influence how AI generates code and handles other development tasks. Instead of manually including context in every chat prompt, specify custom instructions in a Markdown file to ensure consistent AI responses that align with your coding practices and project requirements.

You can configure custom instructions to apply automatically to all chat requests or to specific files only. Alternatively, you can manually attach custom instructions to a specific chat prompt.

> **Note**: Custom instructions are not taken into account for code completions as you type in the editor.

## Type of instructions files
VS Code supports multiple types of Markdown-based instructions files. If you have multiple types of instructions files in your project, VS Code combines and adds them to the chat context, no specific order is guaranteed.

**A single .github/copilot-instructions.md file**

- Automatically applies to all chat requests in the workspace
- Stored within the workspace

**One or more .instructions.md files**

- Created for specific tasks or files
- Use applyTo frontmatter to define what files the instructions should be applied to
- Stored in the workspace or user profile

**A single AGENTS.md file (experimental)**

- Useful if you work with multiple AI agents in your workspace
- Automatically applies to all chat requests in the workspace
- Stored in the root of the workspace
Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.

To reference specific context in your instructions, such as files or URLs, you can use Markdown links.

## Custom instructions examples
The following examples demonstrate how to use custom instructions. For more community-contributed examples, see the Awesome Copilot repository.

- Example: General coding guidelines
- Example: Language-specific coding guidelines
- Example: Documentation writing guidelines

## Use a .github/copilot-instructions.md file
Define your custom instructions in a single .github/copilot-instructions.md Markdown file in the root of your workspace. VS Code applies the instructions in this file automatically to all chat requests within this workspace.

To use a .github/copilot-instructions.md file:

1. Enable the `github.copilot.chat.codeGeneration.useInstructionFiles` setting.

2. Create a `.github/copilot-instructions.md` file at the root of your workspace. If needed, create a `.github` directory first.

3. Describe your instructions by using natural language and in Markdown format.

> **Note**: GitHub Copilot in Visual Studio and GitHub.com also detect the `.github/copilot-instructions.md` file. If you have a workspace that you use in both VS Code and Visual Studio, you can use the same file to define custom instructions for both editors.

## Use .instructions.md files
Instead of using a single instructions file that applies to all chat requests, you can create multiple .instructions.md files that apply to specific file types or tasks. For example, you can create instructions files for different programming languages, frameworks, or project types.

By using the applyTo frontmatter property in the instructions file header, you can specify a glob pattern to define which files the instructions should be applied to automatically. Instructions files are used when creating or modifying files and are typically not applied for read operations.

Alternatively, you can manually attach an instructions file to a specific chat prompt by using the Add Context > Instructions option in the Chat view.

Workspace instructions files: are only available within the workspace and are stored in the .github/instructions folder of the workspace.
User instructions files: are available across multiple workspaces and are stored in the current VS Code profile.

### Instructions file format
Instructions files use the `.instructions.md` extension and have this structure:

**Header (optional): YAML frontmatter**

- `description`: Description shown on hover in Chat view
- `applyTo`: Glob pattern for automatic application (use `**` for all files)

**Body**: Instructions in Markdown format

Example:

```markdown
---
applyTo: "**/*.py"
---
# Project coding standards for Python
- Follow the PEP 8 style guide for Python.
- Always prioritize readability and clarity.
- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Maintain proper indentation (use 4 spaces for each level of indentation).
```

### Create an instructions file
When you create an instructions file, choose whether to store it in your workspace or user profile. Workspace instructions files apply only to that workspace, while user instructions files are available across multiple workspaces.

To create an instructions file:

1. In the Chat view, select **Configure Chat > Instructions**, and then select **New instruction file**.

2. Alternatively, use the **Chat: New Instructions File** command from the Command Palette (`⇧⌘P`).

3. Choose the location where to create the instructions file:

   - **Workspace**: By default, workspace instructions files are stored in the `.github/instructions` folder of your workspace. Add more instruction folders for your workspace with the `chat.instructionsFilesLocations` setting.
   - **User profile**: User instructions files are stored in the current profile folder. You can sync your user instructions files across multiple devices by using Settings Sync.

4. Enter a name for your instructions file.

5. Author the custom instructions by using Markdown formatting.

6. Specify the `applyTo` metadata property in the header to configure when the instructions should be applied automatically. For example, you can specify `applyTo: "**/*.ts,**/*.tsx"` to apply the instructions only to TypeScript files.

7. To reference additional workspace files, use Markdown links (`[index](../index.ts)`).

To modify an existing instructions file, in the Chat view, select Configure Chat > Instructions, and then select an instructions file from the list. Alternatively, use the Chat: Configure Instructions command from the Command Palette (⇧⌘P) and select the instructions file from the Quick Pick.

## Use an AGENTS.md file
If you work with multiple AI agents in your workspace, you can define custom instructions for all agents in an AGENTS.md Markdown file at the root(s) of the workspace. VS Code applies the instructions in this file automatically to all chat requests within this workspace.

To enable or disable support for AGENTS.md files, configure the chat.useAgentsMdFile setting.

### Use multiple AGENTS.md files (experimental)
Using multiple AGENTS.md files in subfolders is useful if you want to apply different instructions to different parts of your project. For example, you can have one AGENTS.md file for the frontend code and another for the backend code.

Use the experimental chat.useNestedAgentsMdFiles setting to enable or disable support for nested AGENTS.md files in your workspace.

When enabled, VS Code searches recursively in all subfolders of your workspace for AGENTS.md files and adds their relative path to the chat context. The agent can then decide which instructions to use based on the files being edited.

> **Tip**: For folder-specific instructions, you can also use multiple `.instructions.md` files with different `applyTo` patterns that match the folder structure.

## Specify custom instructions in settings
You can configure custom instructions for specialized scenarios by using VS Code user or workspace settings.

| Type of instruction	| Setting name
| --- | ---
| Code review	| github.copilot.chat.reviewSelection.instructions
| Commit message generation	| github.copilot.chat.commitMessageGeneration.instructions
| Pull request title and description generation	| github.copilot.chat.pullRequestDescriptionGeneration.instructions
| Code generation (deprecated)*	| github.copilot.chat.codeGeneration.instructions
| Test generation (deprecated)*	| github.copilot.chat.testGeneration.instructions
\* The `codeGeneration` and `testGeneration` settings are deprecated as of VS Code 1.102. We recommend that you use instructions files instead (`.github/copilot-instructions.md` or `*.instructions.md`).

You can define the custom instructions as text in the settings value (text property) or reference an external file (file property) in your workspace.

The following code snippet shows how to define a set of instructions in the settings.json file.

{
  "github.copilot.chat.pullRequestDescriptionGeneration.instructions": [
    { "text": "Always include a list of key changes." }
  ],
  "github.copilot.chat.reviewSelection.instructions": [
    { "file": "guidance/backend-review-guidelines.md" },
    { "file": "guidance/frontend-review-guidelines.md" }
  ]
}
## Generate an instructions file for your workspace
VS Code can analyze your workspace and generate a matching .github/copilot-instructions.md file with custom instructions that match your coding practices and project structure.

To generate an instructions file for your workspace:

1. In the Chat view, select **Configure Chat > Generate Instructions**.

2. Review the generated instructions file and make any necessary edits.

## Sync user instructions files across devices
VS Code can sync your user instructions files across multiple devices by using Settings Sync.

To sync your user instructions files, enable Settings Sync for prompt and instruction files:

1. Make sure you have Settings Sync enabled.

2. Run **Settings Sync: Configure** from the Command Palette (`⇧⌘P`).

3. Select **Prompts and Instructions** from the list of settings to sync.

## Tips for defining custom instructions
- Keep your instructions short and self-contained. Each instruction should be a single, simple statement. If you need to provide multiple pieces of information, use multiple instructions.

- For task or language-specific instructions, use multiple `*.instructions.md` files per topic and apply them selectively by using the `applyTo` property.

- Store project-specific instructions in your workspace to share them with other team members and include them in your version control.

- Reuse and reference instructions files in your prompt files and chat modes to keep them clean and focused, and to avoid duplicating instructions.

## Related Topics

- [Customize AI responses overview](../ai-responses-overview)
- [Create reusable prompt files](../prompt-files)
- [Create custom chat modes](../chat-modes)
- [Get started with chat in VS Code](../chat-getting-started)
- [Configure tools in chat](../chat-tools)
- [Community contributed instructions, prompts, and chat modes](../community-contributions)