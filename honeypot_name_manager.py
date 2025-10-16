import json
import os

class ContainerNameManager:
    def __init__(self, state_file="container_state.json"):
        self.state_file = state_file
        
        # Predefined container names for each config number
        self.containers = {
            1: ["honeypot1a", "honeypot1b", "honeypot1c", "honeypot1d"],
            2: ["honeypot2a", "honeypot2b", "honeypot2c", "honeypot2d"],
            3: ["honeypot3a", "honeypot3b", "honeypot3c", "honeypot3d"],
        }

        # Load in-use state if available
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.in_use = {int(k): v for k, v in json.load(f).items()}  # convert keys back to int
        else:
            self.in_use = {cfg: [] for cfg in self.containers}
            self._save_state()

    def _save_state(self):
        """Save current state to file (convert int keys to strings for JSON)."""
        with open(self.state_file, "w") as f:
            json.dump({str(k): v for k, v in self.in_use.items()}, f, indent=4)

    def get_available_name(self, config):
        """Return an available container name for the given numeric config (1, 2, or 3)."""
        if config not in self.containers:
            raise ValueError("Invalid config number. Use 1, 2, or 3.")

        for name in self.containers[config]:
            if name not in self.in_use[config]:
                self.in_use[config].append(name)
                self._save_state()
                return name
        return None

    def release_name(self, config, name):
        """Mark a container name as available again."""
        if config not in self.in_use:
            raise ValueError("Invalid config number. Use 1, 2, or 3.")
        if name in self.in_use[config]:
            self.in_use[config].remove(name)
            self._save_state()
            return True
        return False

    def list_in_use(self):
        """List all names currently in use."""
        return self.in_use

    def list_available(self, config):
        """List available names for a given numeric config."""
        return [n for n in self.containers[config] if n not in self.in_use[config]]



