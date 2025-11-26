"""
LiveSearch Settings Node
Handles search configuration separately from API and main logic
"""

class LiveSearch_Settings:
    """
    Search Settings Node
    Configures search behavior and optimization options
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["T2T", "TI2T"], {"default": "T2T"}),
                "enable_web_search": ("BOOLEAN", {"default": True, "label_on": "Web Search ON", "label_off": "Web Search OFF"}),
                "num_results": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
                "output_language": (["中文", "English"], {"default": "中文"}),
                "optimize_query": ("BOOLEAN", {"default": True, "label_on": "Query Optimization ON", "label_off": "Query Optimization OFF"}),
            },
            "optional": {
                "proxy": ("STRING", {"default": "", "placeholder": "http://127.0.0.1:7890 (Optional)"}),
            }
        }
    
    RETURN_TYPES = ("SEARCH_SETTINGS",)
    RETURN_NAMES = ("search_settings",)
    FUNCTION = "load_settings"
    CATEGORY = "LiveSearch"
    
    def load_settings(self, mode, enable_web_search, num_results, output_language, optimize_query, proxy=""):
        """
        Load search settings
        Returns a settings dict that can be passed to the search agent
        """
        normalized_mode = mode if mode in ("T2T", "TI2T") else "T2T"
        
        search_settings = {
            "mode": normalized_mode,
            "enable_web_search": enable_web_search,
            "num_results": num_results,
            "output_language": output_language,
            "optimize_query": optimize_query,
            "proxy": proxy.strip() if proxy else None
        }
        
        mode_label = f"{normalized_mode} mode"
        search_mode = "Web Search" if enable_web_search else "LLM Only (No Search)"
        print(f"[LiveSearch Settings] Configured: {mode_label}, {search_mode}, {num_results} results, Language: {output_language}, Optimize: {optimize_query}")
        
        return (search_settings,)

NODE_CLASS_MAPPINGS = {
    "LiveSearch_Settings": LiveSearch_Settings
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_Settings": "⚙️ Live Search Settings"
}

