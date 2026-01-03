.PHONY: run install uninstall dep clean help

INSTALL_DIR := /usr/local/bin
SCRIPT := claude-usage

help:
	@echo "Usage:"
	@echo "  make dep       Install uv if not present"
	@echo "  make run       Run the script"
	@echo "  make install   Install to $(INSTALL_DIR)"
	@echo "  make uninstall Remove from $(INSTALL_DIR)"
	@echo "  make clean     Remove cache files"

dep:
	@command -v uv >/dev/null 2>&1 || { \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	}
	@echo "uv is installed: $$(uv --version)"

run: dep
	@uv run ./$(SCRIPT) compact

install: dep
	@chmod +x $(SCRIPT)
	@sudo cp $(SCRIPT) $(INSTALL_DIR)/
	@echo "Installed to $(INSTALL_DIR)/$(SCRIPT)"
	@echo ""
	@echo "Add to ~/.claude/settings.json:"
	@echo '  { "statusline": { "command": "$(INSTALL_DIR)/$(SCRIPT) compact" } }'

uninstall:
	@sudo rm -f $(INSTALL_DIR)/$(SCRIPT)
	@echo "Removed $(INSTALL_DIR)/$(SCRIPT)"

clean:
	@rm -f /tmp/claude_usage_cache.txt /tmp/claude_usage_cache.lock
	@echo "Cache cleared"
