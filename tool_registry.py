"""
Comprehensive tool registry for Portia AI integrations
Manages database, CRM, and custom tools with authentication
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import all tool modules
from tool_data import fetch_and_summarize_data
from tool_email import send_email
from tool_database import get_database_tools, test_database_connection
from tool_crm import get_crm_tools, test_crm_connection

# Optional Portia imports with graceful fallback
try:
    from portia import tool, ToolRegistry, Config, LLMProvider, Portia
    PORTIA_AVAILABLE = True
except ImportError:
    PORTIA_AVAILABLE = False
    
    # Fallback classes when Portia is not available
    def tool(func):
        """Fallback tool decorator"""
        func._is_tool = True
        return func
    
    class ToolRegistry:
        """Fallback tool registry"""
        def __init__(self, tools):
            self.tools = tools
    
    class Config:
        """Fallback config"""
        @staticmethod
        def from_default(**kwargs):
            return {}
    
    class Portia:
        """Fallback Portia class"""
        def __init__(self, **kwargs):
            pass

# Load environment variables
load_dotenv()

class IntegratedToolRegistry:
    """
    Comprehensive tool registry that manages all AI Workbench tools
    with Portia's authentication and state management
    """
    
    def __init__(self):
        self.tools = {}
        self.tool_categories = {
            'data': [],
            'email': [],
            'database': [],
            'crm': [],
            'system': []
        }
        self.portia_registry = None
        self.config = None
        self._initialize_tools()
        self._setup_portia()
    
    def _initialize_tools(self):
        """Initialize all available tools by category"""
        
        # Data processing tools
        self.tools['fetch_and_summarize_data'] = fetch_and_summarize_data
        self.tool_categories['data'].append('fetch_and_summarize_data')
        
        # Email tools
        self.tools['send_email'] = send_email
        self.tool_categories['email'].append('send_email')
        
        # Database tools
        for tool_func in get_database_tools():
            tool_name = tool_func.__name__
            self.tools[tool_name] = tool_func
            self.tool_categories['database'].append(tool_name)
        
        # CRM tools
        for tool_func in get_crm_tools():
            tool_name = tool_func.__name__
            self.tools[tool_name] = tool_func
            self.tool_categories['crm'].append(tool_name)
        
        # System tools
        self.tools['test_database_connection'] = test_database_connection
        self.tools['test_crm_connection'] = test_crm_connection
        self.tool_categories['system'].extend(['test_database_connection', 'test_crm_connection'])
    
    def _setup_portia(self):
        """Setup Portia configuration and tool registry"""
        if not PORTIA_AVAILABLE:
            print("Warning: Portia SDK not available. Using fallback mode.")
            return
        
        try:
            # Initialize Portia config
            self.config = Config.from_default(
                llm_provider=LLMProvider.OPENAI,
                default_model="gpt-4",
                openai_api_key=os.getenv('OPENAI_API_KEY'),
            )
            
            # Create Portia tool registry with tool instances
            tool_instances = []
            for tool_name, tool_func in self.tools.items():
                try:
                    # Create tool instance for Portia
                    tool_instances.append(tool_func())
                except Exception as e:
                    print(f"Warning: Could not instantiate tool {tool_name}: {e}")
            
            self.portia_registry = ToolRegistry(tool_instances)
            
            print(f"✅ Portia tool registry initialized with {len(tool_instances)} tools")
            
        except Exception as e:
            print(f"Warning: Portia setup failed: {e}")
            self.config = None
            self.portia_registry = None
    
    def get_portia_instance(self) -> Optional[Portia]:
        """Get configured Portia instance with all tools"""
        if not PORTIA_AVAILABLE or not self.config or not self.portia_registry:
            return None
        
        try:
            return Portia(
                config=self.config,
                tools=self.portia_registry
            )
        except Exception as e:
            print(f"Error creating Portia instance: {e}")
            return None
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tool names by category"""
        return self.tool_categories.get(category, [])
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all registered tools"""
        return self.tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def list_available_integrations(self) -> Dict[str, Any]:
        """List all available integrations and their status"""
        integrations = {
            "databases": {
                "postgresql": {
                    "available": True,
                    "configured": bool(os.getenv('POSTGRES_HOST')),
                    "tools": ["query_postgres_database", "get_database_schema"]
                },
                "mysql": {
                    "available": True,
                    "configured": bool(os.getenv('MYSQL_HOST')),
                    "tools": ["query_mysql_database", "get_database_schema"]
                },
                "sqlite": {
                    "available": True,
                    "configured": True,  # SQLite doesn't need external config
                    "tools": ["query_sqlite_database", "get_database_schema"]
                }
            },
            "crm": {
                "salesforce": {
                    "available": True,
                    "configured": bool(os.getenv('SALESFORCE_ACCESS_TOKEN')),
                    "tools": ["get_salesforce_contacts", "create_salesforce_lead"]
                },
                "hubspot": {
                    "available": True,
                    "configured": bool(os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HUBSPOT_API_KEY')),
                    "tools": ["get_hubspot_contacts", "create_hubspot_contact"]
                },
                "zendesk": {
                    "available": True,
                    "configured": bool(os.getenv('ZENDESK_SUBDOMAIN') and os.getenv('ZENDESK_EMAIL')),
                    "tools": ["get_zendesk_tickets", "create_zendesk_ticket"]
                }
            },
            "communication": {
                "email": {
                    "available": True,
                    "configured": True,  # Email tool works in demo mode
                    "tools": ["send_email"]
                }
            },
            "data_processing": {
                "file_analysis": {
                    "available": True,
                    "configured": True,
                    "tools": ["fetch_and_summarize_data"]
                }
            }
        }
        
        return {
            "integrations": integrations,
            "portia_available": PORTIA_AVAILABLE,
            "total_tools": len(self.tools),
            "tool_categories": {k: len(v) for k, v in self.tool_categories.items()},
            "timestamp": datetime.now().isoformat()
        }
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all configured integrations"""
        results = {
            "database_tests": {},
            "crm_tests": {},
            "overall_status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test database connections
        for db_type in ['postgres', 'mysql', 'sqlite']:
            try:
                result = test_database_connection(db_type)
                results["database_tests"][db_type] = result
            except Exception as e:
                results["database_tests"][db_type] = {"error": str(e), "status": "failed"}
        
        # Test CRM connections
        for crm_type in ['salesforce', 'hubspot', 'zendesk']:
            try:
                result = test_crm_connection(crm_type)
                results["crm_tests"][crm_type] = result
            except Exception as e:
                results["crm_tests"][crm_type] = {"error": str(e), "status": "failed"}
        
        # Check overall status
        all_tests = list(results["database_tests"].values()) + list(results["crm_tests"].values())
        if any(test.get("status") == "failed" for test in all_tests):
            results["overall_status"] = "partial"
        
        return results

# Create global tool registry instance
tool_registry = IntegratedToolRegistry()

# Export convenience functions
def get_tool_registry() -> IntegratedToolRegistry:
    """Get the global tool registry instance"""
    return tool_registry

def get_portia_tools() -> Optional[ToolRegistry]:
    """Get Portia tool registry for direct use"""
    return tool_registry.portia_registry

def get_portia_instance() -> Optional[Portia]:
    """Get configured Portia instance"""
    return tool_registry.get_portia_instance()

# Additional utility functions for the main application
@tool
def list_integrations() -> Dict[str, Any]:
    """
    List all available integrations and their configuration status.
    Useful for understanding what tools are available for plan generation.
    """
    return tool_registry.list_available_integrations()

@tool
def test_integrations() -> Dict[str, Any]:
    """
    Test all configured integrations to verify connectivity.
    Helps diagnose authentication and connection issues.
    """
    return tool_registry.test_all_connections()

# Register utility tools
tool_registry.tools['list_integrations'] = list_integrations
tool_registry.tools['test_integrations'] = test_integrations
tool_registry.tool_categories['system'].extend(['list_integrations', 'test_integrations'])

# Recreate Portia registry if it was created before registering utility tools
if PORTIA_AVAILABLE and tool_registry.portia_registry:
    try:
        tool_instances = []
        for tool_name, tool_func in tool_registry.tools.items():
            try:
                tool_instances.append(tool_func())
            except Exception as e:
                print(f"Warning: Could not instantiate tool {tool_name}: {e}")
        
        tool_registry.portia_registry = ToolRegistry(tool_instances)
        print(f"✅ Portia tool registry updated with {len(tool_instances)} tools")
    except Exception as e:
        print(f"Warning: Could not update Portia registry: {e}")

if __name__ == "__main__":
    # Test the tool registry when run directly
    print("🔧 AI Workbench Tool Registry")
    print("=" * 50)
    
    integrations = tool_registry.list_available_integrations()
    print(f"Total tools: {integrations['total_tools']}")
    print(f"Portia available: {integrations['portia_available']}")
    print("\nTool categories:")
    for category, count in integrations['tool_categories'].items():
        print(f"  {category}: {count} tools")
    
    print("\n🧪 Testing connections...")
    test_results = tool_registry.test_all_connections()
    print(f"Overall status: {test_results['overall_status']}")
    
    # Test Portia instance creation
    if PORTIA_AVAILABLE:
        portia_instance = tool_registry.get_portia_instance()
        if portia_instance:
            print("✅ Portia instance created successfully")
        else:
            print("❌ Failed to create Portia instance")
    else:
        print("⚠️ Portia SDK not available")
