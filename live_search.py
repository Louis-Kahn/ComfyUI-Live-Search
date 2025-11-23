import os
import json
import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS
from .config_manager import ConfigManager

# Initialize Config Manager
config_manager = ConfigManager()

class SearchTool:
    @staticmethod
    def search_google(query, num_results=3):
        """
        Performs a Google search and returns a list of dicts consistent with DDG format.
        """
        try:
            # googlesearch-python generator
            results = list(google_search(query, num_results=num_results, advanced=True))
            # Normalize to list of dicts: {'title', 'url', 'summary'}
            normalized_results = []
            for res in results:
                normalized_results.append({
                    'title': res.title,
                    'url': res.url,
                    'summary': res.description
                })
            return normalized_results
        except Exception as e:
            print(f"[LiveSearch] Google Search error: {e}")
            return []

    @staticmethod
    def search_duckduckgo(query, num_results=3):
        """
        Performs a DuckDuckGo search.
        """
        try:
            with DDGS() as ddgs:
                # ddgs.text() returns a generator of dicts: {'title', 'href', 'body'}
                results = list(ddgs.text(query, max_results=num_results))
            
            # Normalize keys to match Google
            normalized_results = []
            for res in results:
                normalized_results.append({
                    'title': res.get('title', ''),
                    'url': res.get('href', ''),
                    'summary': res.get('body', '')
                })
            return normalized_results
        except Exception as e:
            print(f"[LiveSearch] DuckDuckGo Search error: {e}")
            return []

    @staticmethod
    def fetch_url_content(url, timeout=10):
        """
        Fetches and extracts text content from a URL.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid context overflow (simple truncation)
            return text[:5000] 
            
        except Exception as e:
            print(f"[LiveSearch] Fetch error for {url}: {e}")
            return ""

class LLMClient:
    @staticmethod
    def chat_completion(api_key, base_url, model, messages, temperature=0.7):
        """
        Generic OpenAI-compatible chat completion
        """
        if not api_key:
            return "Error: API Key is missing."
            
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            # Increased timeout to 120s as DeepSeek R1/V3 can be slow sometimes
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

class LiveSearchNode:
    """
    A ComfyUI node that performs a web search and summarizes the results using an LLM.
    Ideal for retrieving real-time information like weather, news, etc.
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "e.g., What is the weather in Tokyo right now? or just 35.6762, 139.6503"}),
                "mode": (["Smart Search (Auto-Query)", "Direct Search", "Weather/Time Mode"], {"default": "Smart Search (Auto-Query)"}),
                "search_engine": (["DuckDuckGo", "Google"], {"default": "DuckDuckGo"}),
                "provider": ([
                    "OpenAI", 
                    "DeepSeek (Official)", 
                    "DeepSeek (Aliyun)", 
                    "DeepSeek (Volcengine)",
                    "Gemini (OpenAI-Format)", 
                    "Custom"
                ], {"default": "DeepSeek (Official)"}),
                "model": ("STRING", {"default": "deepseek-chat", "multiline": False, "placeholder": "Model Name (e.g. deepseek-chat, deepseek-r1)"}),
                "num_results": ("INT", {"default": 3, "min": 1, "max": 10}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "placeholder": "Leave empty to use config file"}),
                "custom_base_url": ("STRING", {"default": "", "placeholder": "Required for Custom/Gemini/DeepSeek"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("answer", "source_urls")
    FUNCTION = "process_search"
    CATEGORY = "LiveSearch"

    def process_search(self, prompt, mode, search_engine, provider, model, num_results, api_key, custom_base_url):
        # 1. Resolve API Key and Base URL
        resolved_api_key = api_key.strip()
        if not resolved_api_key:
             # Fallback to config file if UI input is empty
             resolved_api_key = config_manager.get_api_key(provider, "")
        
        # Default to OpenAI
        base_url = "https://api.openai.com/v1"
        final_model = model

        # --- Provider Logic ---
        if provider == "DeepSeek (Official)":
            base_url = "https://api.deepseek.com"
            # Official usually uses 'deepseek-chat' or 'deepseek-reasoner'
        
        elif provider == "DeepSeek (Aliyun)":
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            # Aliyun might need specific model mapping if user didn't input exact one, 
            # but usually we trust the user's input or provide a smart default.
            # If user left default 'deepseek-chat', Aliyun calls it 'deepseek-v3' usually.
            if final_model == "deepseek-chat":
                final_model = "deepseek-v3"

        elif provider == "DeepSeek (Volcengine)":
            base_url = "https://ark.cn-beijing.volces.com/api/v3"
            # Volcengine uses Endpoint IDs (e.g. ep-2025...) as model names usually, 
            # or mapped names if configured. The user needs to input the correct endpoint ID or model name.
            
        elif provider == "Gemini (OpenAI-Format)":
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        
        if custom_base_url.strip():
            base_url = custom_base_url.strip()
        
        # 2. Determine Search Query
        search_query = prompt
        
        if mode == "Weather/Time Mode":
            search_query = f"current time and weather at location {prompt}"
        
        elif mode == "Smart Search (Auto-Query)":
            refine_messages = [
                {"role": "system", "content": "You are a search engine expert. Convert the user's input into the single best search query to find the answer. Return ONLY the query, no quotes."},
                {"role": "user", "content": prompt}
            ]
            refined_query = LLMClient.chat_completion(resolved_api_key, base_url, final_model, refine_messages)
            if not refined_query.startswith("Error"):
                print(f"[LiveSearch] Refined query: {prompt} -> {refined_query}")
                search_query = refined_query

        # 3. Perform Search
        print(f"[LiveSearch] Searching for: {search_query} using {search_engine}")
        
        if search_engine == "Google":
            search_results = SearchTool.search_google(search_query, num_results)
        else:
            search_results = SearchTool.search_duckduckgo(search_query, num_results)
        
        if not search_results:
            return (f"No search results found using {search_engine}.", "")

        # 4. Extract Content
        context_data = []
        source_urls = []
        
        for res in search_results:
            url = res['url']
            title = res['title']
            summary = res['summary']
            
            print(f"[LiveSearch] Fetching: {url}")
            content = SearchTool.fetch_url_content(url)
            
            if content:
                snippet = content[:2000] if content else summary
                context_data.append(f"Source: {title} ({url})\nSummary: {summary}\nContent: {snippet}\n---")
                source_urls.append(url)
        
        full_context = "\n".join(context_data)

        # 5. Generate Answer
        system_prompt = "You are a helpful assistant with access to real-time web search results. Answer the user's original prompt based ONLY on the provided search results. If the results contain time or weather info, be precise."
        
        if mode == "Weather/Time Mode":
            system_prompt += " The user specifically wants to know the local time and weather conditions."

        final_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {prompt}\n\nSearch Results:\n{full_context}"}
        ]

        answer = LLMClient.chat_completion(resolved_api_key, base_url, final_model, final_messages)
        
        return (answer, "\n".join(source_urls))
