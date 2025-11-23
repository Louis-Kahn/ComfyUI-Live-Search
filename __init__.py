from .live_search import LiveSearchNode

NODE_CLASS_MAPPINGS = {
    "LiveSearchNode": LiveSearchNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearchNode": "🌐 Live Search Agent"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

