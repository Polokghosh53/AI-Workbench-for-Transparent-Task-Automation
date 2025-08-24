"""
CRM integration tools for Portia AI
Provides authenticated CRM operations for Salesforce, HubSpot, and other CRM systems
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Annotated
from datetime import datetime
from dotenv import load_dotenv

# Optional Portia imports with graceful fallback
try:
    from portia import tool, ToolRegistry
    PORTIA_AVAILABLE = True
except ImportError:
    PORTIA_AVAILABLE = False
    
    # Fallback decorator when Portia is not available
    def tool(func):
        """Fallback tool decorator"""
        func._is_tool = True
        return func
    
    class ToolRegistry:
        """Fallback tool registry"""
        def __init__(self, tools):
            self.tools = tools

# Load environment variables
load_dotenv()

class CRMConfig:
    """CRM configuration manager with authentication"""
    
    def __init__(self):
        # Salesforce configuration
        self.salesforce_config = {
            'instance_url': os.getenv('SALESFORCE_INSTANCE_URL', 'https://your-instance.salesforce.com'),
            'access_token': os.getenv('SALESFORCE_ACCESS_TOKEN', ''),
            'client_id': os.getenv('SALESFORCE_CLIENT_ID', ''),
            'client_secret': os.getenv('SALESFORCE_CLIENT_SECRET', ''),
            'username': os.getenv('SALESFORCE_USERNAME', ''),
            'password': os.getenv('SALESFORCE_PASSWORD', ''),
            'security_token': os.getenv('SALESFORCE_SECURITY_TOKEN', '')
        }
        
        # HubSpot configuration
        self.hubspot_config = {
            'api_key': os.getenv('HUBSPOT_API_KEY', ''),
            'access_token': os.getenv('HUBSPOT_ACCESS_TOKEN', ''),
            'base_url': 'https://api.hubapi.com'
        }
        
        # Zendesk configuration
        self.zendesk_config = {
            'subdomain': os.getenv('ZENDESK_SUBDOMAIN', ''),
            'email': os.getenv('ZENDESK_EMAIL', ''),
            'token': os.getenv('ZENDESK_TOKEN', ''),
            'base_url': f"https://{os.getenv('ZENDESK_SUBDOMAIN', 'your-subdomain')}.zendesk.com/api/v2"
        }

crm_config = CRMConfig()

@tool
def get_salesforce_contacts(
    limit: Annotated[int, "Maximum number of contacts to retrieve"] = 10,
    search_term: Annotated[Optional[str], "Search term to filter contacts"] = None
) -> Dict[str, Any]:
    """
    Retrieve contacts from Salesforce CRM with authentication.
    Returns contact information including names, emails, and phone numbers.
    """
    try:
        if not crm_config.salesforce_config['access_token']:
            return {
                "error": "Salesforce authentication required",
                "message": "Please configure SALESFORCE_ACCESS_TOKEN in environment variables",
                "status": "failed",
                "crm": "Salesforce"
            }
        
        headers = {
            'Authorization': f"Bearer {crm_config.salesforce_config['access_token']}",
            'Content-Type': 'application/json'
        }
        
        # Build SOQL query
        fields = "Id, Name, Email, Phone, Account.Name, CreatedDate, LastModifiedDate"
        soql = f"SELECT {fields} FROM Contact"
        
        if search_term:
            soql += f" WHERE Name LIKE '%{search_term}%' OR Email LIKE '%{search_term}%'"
        
        soql += f" ORDER BY LastModifiedDate DESC LIMIT {limit}"
        
        url = f"{crm_config.salesforce_config['instance_url']}/services/data/v52.0/query"
        params = {'q': soql}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "data": data.get('records', []),
                "total_size": data.get('totalSize', 0),
                "timestamp": datetime.now().isoformat(),
                "crm": "Salesforce",
                "query": soql
            }
        else:
            return {
                "error": "Salesforce API error",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "Salesforce"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "Salesforce"
        }

@tool
def create_salesforce_lead(
    first_name: Annotated[str, "Lead's first name"],
    last_name: Annotated[str, "Lead's last name"],
    email: Annotated[str, "Lead's email address"],
    company: Annotated[str, "Lead's company name"],
    phone: Annotated[Optional[str], "Lead's phone number"] = None,
    lead_source: Annotated[Optional[str], "Source of the lead"] = None
) -> Dict[str, Any]:
    """
    Create a new lead in Salesforce CRM with authentication.
    Returns the created lead ID and details.
    """
    try:
        if not crm_config.salesforce_config['access_token']:
            return {
                "error": "Salesforce authentication required",
                "message": "Please configure SALESFORCE_ACCESS_TOKEN in environment variables",
                "status": "failed",
                "crm": "Salesforce"
            }
        
        headers = {
            'Authorization': f"Bearer {crm_config.salesforce_config['access_token']}",
            'Content-Type': 'application/json'
        }
        
        lead_data = {
            'FirstName': first_name,
            'LastName': last_name,
            'Email': email,
            'Company': company
        }
        
        if phone:
            lead_data['Phone'] = phone
        if lead_source:
            lead_data['LeadSource'] = lead_source
        
        url = f"{crm_config.salesforce_config['instance_url']}/services/data/v52.0/sobjects/Lead"
        
        response = requests.post(url, headers=headers, json=lead_data)
        
        if response.status_code == 201:
            data = response.json()
            return {
                "status": "success",
                "data": {
                    "id": data.get('id'),
                    "lead_data": lead_data,
                    "created": True
                },
                "timestamp": datetime.now().isoformat(),
                "crm": "Salesforce"
            }
        else:
            return {
                "error": "Failed to create lead",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "Salesforce"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "Salesforce"
        }

@tool
def get_hubspot_contacts(
    limit: Annotated[int, "Maximum number of contacts to retrieve"] = 10,
    search_term: Annotated[Optional[str], "Search term to filter contacts"] = None
) -> Dict[str, Any]:
    """
    Retrieve contacts from HubSpot CRM with authentication.
    Returns contact information including names, emails, and properties.
    """
    try:
        if not crm_config.hubspot_config['access_token'] and not crm_config.hubspot_config['api_key']:
            return {
                "error": "HubSpot authentication required",
                "message": "Please configure HUBSPOT_ACCESS_TOKEN or HUBSPOT_API_KEY in environment variables",
                "status": "failed",
                "crm": "HubSpot"
            }
        
        # Set up authentication
        headers = {'Content-Type': 'application/json'}
        params = {'limit': limit}
        
        if crm_config.hubspot_config['access_token']:
            headers['Authorization'] = f"Bearer {crm_config.hubspot_config['access_token']}"
        else:
            params['hapikey'] = crm_config.hubspot_config['api_key']
        
        # Add properties to retrieve
        properties = ['firstname', 'lastname', 'email', 'phone', 'company', 'createdate', 'lastmodifieddate']
        params['properties'] = ','.join(properties)
        
        url = f"{crm_config.hubspot_config['base_url']}/crm/v3/objects/contacts"
        
        if search_term:
            # Use search API for filtered results
            search_url = f"{crm_config.hubspot_config['base_url']}/crm/v3/objects/contacts/search"
            search_data = {
                "filterGroups": [{
                    "filters": [
                        {"propertyName": "email", "operator": "CONTAINS_TOKEN", "value": search_term},
                        {"propertyName": "firstname", "operator": "CONTAINS_TOKEN", "value": search_term},
                        {"propertyName": "lastname", "operator": "CONTAINS_TOKEN", "value": search_term}
                    ]
                }],
                "properties": properties,
                "limit": limit
            }
            response = requests.post(search_url, headers=headers, json=search_data)
        else:
            response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "data": data.get('results', []),
                "total": len(data.get('results', [])),
                "timestamp": datetime.now().isoformat(),
                "crm": "HubSpot"
            }
        else:
            return {
                "error": "HubSpot API error",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "HubSpot"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "HubSpot"
        }

@tool
def create_hubspot_contact(
    email: Annotated[str, "Contact's email address"],
    first_name: Annotated[Optional[str], "Contact's first name"] = None,
    last_name: Annotated[Optional[str], "Contact's last name"] = None,
    phone: Annotated[Optional[str], "Contact's phone number"] = None,
    company: Annotated[Optional[str], "Contact's company name"] = None
) -> Dict[str, Any]:
    """
    Create a new contact in HubSpot CRM with authentication.
    Returns the created contact ID and details.
    """
    try:
        if not crm_config.hubspot_config['access_token'] and not crm_config.hubspot_config['api_key']:
            return {
                "error": "HubSpot authentication required",
                "message": "Please configure HUBSPOT_ACCESS_TOKEN or HUBSPOT_API_KEY in environment variables",
                "status": "failed",
                "crm": "HubSpot"
            }
        
        # Set up authentication
        headers = {'Content-Type': 'application/json'}
        
        if crm_config.hubspot_config['access_token']:
            headers['Authorization'] = f"Bearer {crm_config.hubspot_config['access_token']}"
            params = {}
        else:
            params = {'hapikey': crm_config.hubspot_config['api_key']}
        
        # Build contact properties
        properties = {'email': email}
        if first_name:
            properties['firstname'] = first_name
        if last_name:
            properties['lastname'] = last_name
        if phone:
            properties['phone'] = phone
        if company:
            properties['company'] = company
        
        contact_data = {'properties': properties}
        
        url = f"{crm_config.hubspot_config['base_url']}/crm/v3/objects/contacts"
        
        response = requests.post(url, headers=headers, json=contact_data, params=params)
        
        if response.status_code == 201:
            data = response.json()
            return {
                "status": "success",
                "data": {
                    "id": data.get('id'),
                    "properties": data.get('properties', {}),
                    "created": True
                },
                "timestamp": datetime.now().isoformat(),
                "crm": "HubSpot"
            }
        else:
            return {
                "error": "Failed to create contact",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "HubSpot"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "HubSpot"
        }

@tool
def get_zendesk_tickets(
    limit: Annotated[int, "Maximum number of tickets to retrieve"] = 10,
    status: Annotated[Optional[str], "Ticket status filter (open, pending, solved)"] = None
) -> Dict[str, Any]:
    """
    Retrieve support tickets from Zendesk with authentication.
    Returns ticket information including subject, status, and requester details.
    """
    try:
        if not all([crm_config.zendesk_config['subdomain'], 
                   crm_config.zendesk_config['email'], 
                   crm_config.zendesk_config['token']]):
            return {
                "error": "Zendesk authentication required",
                "message": "Please configure ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_TOKEN",
                "status": "failed",
                "crm": "Zendesk"
            }
        
        # Set up authentication
        auth = (f"{crm_config.zendesk_config['email']}/token", crm_config.zendesk_config['token'])
        headers = {'Content-Type': 'application/json'}
        
        # Build API URL
        url = f"{crm_config.zendesk_config['base_url']}/tickets.json"
        params = {'per_page': limit, 'sort_by': 'updated_at', 'sort_order': 'desc'}
        
        if status:
            params['status'] = status
        
        response = requests.get(url, headers=headers, auth=auth, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "data": data.get('tickets', []),
                "count": data.get('count', 0),
                "timestamp": datetime.now().isoformat(),
                "crm": "Zendesk"
            }
        else:
            return {
                "error": "Zendesk API error",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "Zendesk"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "Zendesk"
        }

@tool
def create_zendesk_ticket(
    subject: Annotated[str, "Ticket subject"],
    description: Annotated[str, "Ticket description/body"],
    requester_email: Annotated[str, "Email of the person requesting support"],
    priority: Annotated[Optional[str], "Ticket priority (low, normal, high, urgent)"] = "normal",
    ticket_type: Annotated[Optional[str], "Ticket type (problem, incident, question, task)"] = "question"
) -> Dict[str, Any]:
    """
    Create a new support ticket in Zendesk with authentication.
    Returns the created ticket ID and details.
    """
    try:
        if not all([crm_config.zendesk_config['subdomain'], 
                   crm_config.zendesk_config['email'], 
                   crm_config.zendesk_config['token']]):
            return {
                "error": "Zendesk authentication required",
                "message": "Please configure ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_TOKEN",
                "status": "failed",
                "crm": "Zendesk"
            }
        
        # Set up authentication
        auth = (f"{crm_config.zendesk_config['email']}/token", crm_config.zendesk_config['token'])
        headers = {'Content-Type': 'application/json'}
        
        # Build ticket data
        ticket_data = {
            "ticket": {
                "subject": subject,
                "comment": {"body": description},
                "requester": {"email": requester_email},
                "priority": priority,
                "type": ticket_type
            }
        }
        
        url = f"{crm_config.zendesk_config['base_url']}/tickets.json"
        
        response = requests.post(url, headers=headers, auth=auth, json=ticket_data)
        
        if response.status_code == 201:
            data = response.json()
            return {
                "status": "success",
                "data": {
                    "ticket": data.get('ticket', {}),
                    "created": True
                },
                "timestamp": datetime.now().isoformat(),
                "crm": "Zendesk"
            }
        else:
            return {
                "error": "Failed to create ticket",
                "message": response.text,
                "status_code": response.status_code,
                "status": "failed",
                "crm": "Zendesk"
            }
    
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "crm": "Zendesk"
        }

# Create CRM tool registry - Pass tool instances when Portia is available
if PORTIA_AVAILABLE:
    try:
        crm_tools = ToolRegistry([
            get_salesforce_contacts(),
            create_salesforce_lead(),
            get_hubspot_contacts(),
            create_hubspot_contact(),
            get_zendesk_tickets(),
            create_zendesk_ticket()
        ])
    except Exception as e:
        print(f"Warning: Could not create Portia CRM tools: {e}")
        crm_tools = None
else:
    crm_tools = None

# Helper functions for non-Portia usage
def get_crm_tools():
    """Get all CRM tools for manual registration"""
    return [
        get_salesforce_contacts,
        create_salesforce_lead,
        get_hubspot_contacts,
        create_hubspot_contact,
        get_zendesk_tickets,
        create_zendesk_ticket
    ]

def test_crm_connection(crm_type: str) -> Dict[str, Any]:
    """Test CRM connection and return status"""
    try:
        if crm_type.lower() == 'salesforce':
            return get_salesforce_contacts(limit=1)
        elif crm_type.lower() == 'hubspot':
            return get_hubspot_contacts(limit=1)
        elif crm_type.lower() == 'zendesk':
            return get_zendesk_tickets(limit=1)
        else:
            return {"error": "Unsupported CRM type", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
