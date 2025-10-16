# honeypot_name_manager.py
import json
import os

class ContainerNameManager:
    def __init__(self, state_file="container_state.json"):
        self.state_file = state_file

        # Predefined container names for each config
        self.containers = {
            "config1": ["honeypot1a", "honeypot1b", "honeypot1c", "honeypot1d"],
            "config2": ["honeypot2a", "honeypot2b", "honeypot2c", "honeypot2d"],
            "config3": ["honeypot3a", "honeypot3b", "honeypot3c", "honeypot3d"],
        }

        # Load in-use state from file (if it exists)
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.in_use = json.load(f)
        else:
            self.in_use = {cfg: [] for cfg in self.containers}
            self._save_state()

    def _save_state(self):
        """Save the current in-use state to a JSON file."""
        with open(self.state_file, "w") as f:
            json.dump(self.in_use, f, indent=4)

    def get_available_name(self, config):
        """Get an unused container name for the given config, and mark it as used."""
        for name in self.containers[config]:
            if name not in self.in_use[config]:
                self.in_use[config].append(name)
                self._save_state()
                return name
        return None  # All names in use

    def release_name(self, config, name):
        """Free up a container name when it's no longer in use."""
        if name in self.in_use[config]:
            self.in_use[config].remove(name)
            self._save_state()
            return True
        return False

    def list_in_use(self):
        """Return a dict of all containers currently in use."""
        return self.in_use

    def list_available(self, config):
        """List names that aren’t currently in use for a given config."""
        return [name for name in self.containers[config] if name not in self.in_use[config]]


# Example usage
if __name__ == "__main__":
    manager = ContainerNameManager()

    # Start a container for config2
    name = manager.get_available_name("config2")
    if name:
        print(f"Starting container: {name}")
    else:
        print("All container names for config2 are in use.")

    # Show in-use names
    print("In use:", manager.list_in_use())

    # Release a container name later
    if name:
        manager.release_name("config2", name)
        print(f"Released: {name}")
        print("Available again:", manager.list_available("config2"))

