# release_all_names.py
from honeypot_name_manager import ContainerNameManager

def release_all():
    manager = ContainerNameManager()
    for config in manager.in_use.keys():
        # Copy the list so we can modify while iterating
        for name in list(manager.in_use[config]):
            manager.release_name(config, name)
            print(f"✅ Released {name} from {config}")
    print("🎉 All container names have been released.")

if __name__ == "__main__":
    release_all()

