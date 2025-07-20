class NodeTracker:
    def __init__(self):
        self.active_node = None

    def update_active_node(self, node_name: str):
        """Update the currently active node for frontend highlighting."""
        print(f"Node in progress: {node_name}")
        self.active_node = node_name

    def get_active_node(self):
        """Get the currently active node."""
        return self.active_node

# Create a global instance
node_tracker = NodeTracker() 