# claude-usage

A statusline script for Claude Code that displays usage limits and context window information.

## Output

```
claude-opus-4-5-20251101 · D:27% (1h) · W:5% (7d) · C:48% (96k/200k)
```

- **D**: Daily usage % (time until reset)
- **W**: Weekly usage % (days until reset)
- **C**: Context window % (tokens used/total)

## Requirements

- Python 3.10+
- `pexpect` library: `pip install pexpect`

## Installation

```bash
# Copy to a location in your PATH
sudo cp claude-usage /usr/local/bin/
sudo chmod +x /usr/local/bin/claude-usage

# Configure Claude Code statusline in ~/.claude/settings.json:
{
  "statusline": {
    "command": "/usr/local/bin/claude-usage compact"
  }
}
```

## Usage

```bash
claude-usage           # Default format with labels
claude-usage compact   # Compact format (recommended for statusline)
claude-usage json      # JSON output
```

## How it works

- Receives context window data from Claude Code via stdin (JSON)
- Fetches usage limits by running `claude /status` via pexpect
- Caches usage data for 5 minutes with background refresh
- First run may be slow; subsequent calls are instant

## Environment Variables

- `DEBUG=1` - Enable debug output
- `CLAUDE_USAGE_HOME` - Directory for running claude commands (default: `~/.claude-usage`)
