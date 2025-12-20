# 🎹 MIDI Agent Skill

**MIDI Agent Skill** is a custom **Agent Skill compatible with Claude Skills**, enabling AI agents to generate MIDI files from natural language music descriptions.

This skill follows the same design and usage pattern as **Claude Custom Skills**:  
it is defined by a directory structure and a `SKILL.md`, and can be uploaded to Claude or used via the Claude API.  
Claude will automatically decide when to invoke the skill based on the user prompt.

---

## 🚀 Features

- 🎼 **Generate MIDI from text prompts**
- 🤖 **Fully compatible with Claude Skills**
- 🧩 **Automatic skill invocation by Claude**
- 📦 **Structured MIDI output**
- 🟦 **TypeScript-based implementation**

---

## 📦 Repository Structure

```

/
├─ skills/           # Skill implementation
├─ types/            # TypeScript types and interfaces
├─ output/           # Generated MIDI artifacts
├─ SKILL.md          # Claude Skill definition and instructions
├─ package.json      # Project metadata and dependencies
└─ README.md         # Documentation

````

---

## 🧠 What Is a Claude Skill?

Claude Skills are modular extensions that allow Claude to perform specialized tasks.

A Skill consists of:
- A directory
- A `SKILL.md` file describing **what the skill does and when to use it**
- Optional scripts, resources, and code

Claude automatically selects and runs the appropriate skill based on the user’s input —  
you do **not** need to explicitly tell Claude to use the skill.

This repository implements a **custom Claude Skill** for MIDI generation.

---

## 📘 Installation (Local Development)

```bash
npm install
````

(Optional build)

```bash
npm run build
```

---

## 🚀 Usage with Claude (UI)

### 1. Enable Skills in Claude

1. Open **Claude Settings**
2. Enable **Skills**
3. Upload this repository as a ZIP file (or select it if already registered)
4. Turn the skill **ON**

Once enabled, the skill becomes available to Claude automatically.

---

### 2. Use the Skill (Automatic Invocation)

Simply ask Claude something related to music or MIDI creation:

```text
Compose an 8-bar piano melody in C major and generate a MIDI file.
```

Claude will:

1. Detect that the request matches this skill
2. Invoke **MIDI Agent Skill**
3. Return structured MIDI output

You do **not** need to mention the skill name explicitly.

---

## 📡 Usage with Claude API

This skill can also be used via the **Claude Messages API** by specifying it in the `container.skills` field.

### Example (Python)

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4096,
    betas=["skills-2025-10-02", "code-execution-2025-08-25"],
    container={
        "skills": [
            {
                "type": "custom",
                "skill_id": "midi-agent-skill",
                "version": "latest"
            }
        ]
    },
    messages=[
        {
            "role": "user",
            "content": "Generate a calm piano MIDI in C major."
        }
    ]
)
```

Claude will automatically invoke the skill when appropriate.

---

## 📄 Skill API

### `generateMIDI`

Generate a MIDI composition from a structured music description.

#### Input Parameters

| Field  | Type   | Description                           |
| ------ | ------ | ------------------------------------- |
| prompt | string | Natural language music description    |
| tempo  | number | Tempo in BPM (optional)               |
| key    | string | Musical key (optional)                |
| length | number | Number of bars or duration (optional) |

#### Output Example

```jsonc
{
  "midiData": "base64-encoded-midi",
  "metadata": {
    "tempo": 120,
    "key": "C",
    "bars": 8
  }
}
```

The returned data can be saved as a `.mid` file or passed to a MIDI playback system.

---

## 📌 Example Prompts

```text
Create a slow ambient synth progression and output it as a MIDI file.
```

```text
Generate a fast jazz-style piano riff in F minor.
```

---

## 🛠️ Development Notes

* `SKILL.md` defines **when and how Claude should use this skill**
* The description section is critical for correct automatic invocation
* Be explicit about:

  * What the skill does
  * When it should be used
  * What kind of output it produces

---

## 🧪 Testing

There is no standalone test runner included.

Recommended testing approach:

1. Upload the skill to Claude
2. Ask music-related prompts
3. Verify that Claude automatically invokes the skill
4. Validate the generated MIDI using a standard MIDI player

---

## 🧩 How It Works

1. **Prompt Analysis**
   Claude analyzes the user request and determines that MIDI generation is required.

2. **Skill Invocation**
   Claude invokes this skill based on the `SKILL.md` description.

3. **Music Structuring**
   The prompt is converted into structured musical intent.

4. **MIDI Encoding**
   The intent is encoded into standard MIDI format.

5. **Result Delivery**
   Structured MIDI data is returned to Claude.
