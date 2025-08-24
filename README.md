# AI Workbench for Transparent Task Automation

> **Powered by Portia AI** - A comprehensive platform for transparent, steerable, and authenticated AI task automation with integrated database and CRM capabilities.

## 🚀 Overview

The AI Workbench is a modern web application that leverages [Portia AI's framework](https://docs.portialabs.ai/) to provide transparent and controllable AI task automation. Built with a focus on business users, it enables secure interactions with databases, CRM systems, and external APIs through an intuitive interface with full audit trails and rollback capabilities.

### ✨ Key Features

- **🔍 Transparent Planning**: Generate and review structured plans before execution using Portia's planning system
- **🛡️ Authenticated Access**: Secure, just-in-time authentication for all integrations
- **🗄️ Database Operations**: Query PostgreSQL, MySQL, and SQLite databases with security validation
- **👥 CRM Integration**: Connect to Salesforce, HubSpot, and Zendesk with full API support
- **📊 Data Analysis**: Upload and analyze files (Excel, CSV, DOCX) with visualizations
- **📧 Smart Email**: Generate and send rich, formatted email reports
- **🔄 Rollback Support**: Undo sensitive operations with Portia's state management
- **📋 Audit Trail**: Complete logging and history of all plan executions
- **⚠️ Clarifications**: Pause execution for human input on sensitive operations

## 🏗️ Tech Stack

### Frontend
- **React 18** - Modern UI with hooks and functional components
- **JavaScript (ES6+)** - Modern JavaScript features
- **CSS3** - Custom styling with CSS variables and grid layouts
- **Axios** - HTTP client for API communication

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.11+** - Modern Python with type hints
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and settings management

### AI & Automation
- **Portia AI SDK** - Core framework for transparent task automation
  - Structured plan generation and execution
  - Just-in-time authentication system
  - State management and rollback capabilities
  - Tool registry and extension system
- **OpenAI GPT-4** - Language model for plan generation (via Portia)

### Database Support
- **PostgreSQL** - Enterprise database with psycopg2-binary driver
- **MySQL** - Popular database with mysql-connector-python
- **SQLite** - Embedded database (zero-config, immediate use)
- **SQL Security** - Query validation and parameter binding

### CRM & External APIs
- **Salesforce** - Lead and contact management via REST API
- **HubSpot** - Customer relationship management via API
- **Zendesk** - Support ticket management via API
- **Requests** - HTTP library for external API calls

### Data Processing
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Matplotlib & Seaborn** - Data visualization
- **OpenPyXL** - Excel file processing
- **python-docx** - Word document processing

### Development & Deployment
- **Node.js & npm** - Frontend build tools
- **Python Virtual Environment** - Dependency isolation
- **Environment Variables** - Secure configuration management
- **Hot Reload** - Development with live updates

## 🎯 How Portia AI Powers the Platform

### Transparent Planning
The application uses [Portia's PlanBuilder](https://docs.portialabs.ai/generate-and-run-plans) to create structured, reviewable plans:

```python
plan_builder = PlanBuilder(query="Analyze sales data and update CRM")
plan_builder.step(
    task="Query database for sales metrics",
    tool_id="query_postgres_database",
    description="Retrieve Q4 sales data with security validation"
)
plan_builder.step(
    task="Update Salesforce with insights",
    tool_id="create_salesforce_lead",
    description="Create qualified leads based on analysis"
)
```

### Authentication & Clarifications
[Portia's clarification system](https://docs.portialabs.ai/handle-auth-clarifications) enables secure, just-in-time authentication:

```python
plan_builder.step(
    task="Review data before sending",
    tool_id="human_review_clarification",
    description="Pause for human approval of sensitive operations"
)
```

### Tool Extensibility
The platform leverages [Portia's tool system](https://docs.portialabs.ai/extend-run-tools) with 16+ integrated tools:

- **Database Tools**: PostgreSQL, MySQL, SQLite query execution
- **CRM Tools**: Salesforce, HubSpot, Zendesk integration
- **Data Tools**: File analysis, visualization, summarization
- **Communication**: Intelligent email generation and sending

### State Management & Security
Following [Portia's production guidelines](https://docs.portialabs.ai/running-in-production):

- **Audit Logs**: Complete execution history with timestamps
- **Rollback Points**: Undo sensitive database or CRM operations
- **Access Control**: User-based authentication and authorization
- **Error Handling**: Graceful degradation and error recovery

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (tested with Python 3.13)
- **Node.js 16+** and npm
- **Git** for cloning the repository

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AI-Workbench-for-Transparent-Task-Automation.git
   cd AI-Workbench-for-Transparent-Task-Automation
   ```

2. **Set up the backend**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend**:
   ```bash
   npm install
   ```

4. **Configure environment** (optional for basic use):
   ```bash
   # Copy configuration template
   cp env.example .env
   
   # Edit .env with your API keys (optional - SQLite works immediately)
   # OPENAI_API_KEY=your_openai_key_here
   # SALESFORCE_ACCESS_TOKEN=your_salesforce_token
   # HUBSPOT_API_KEY=your_hubspot_key
   ```

### Running the Application

1. **Start the backend**:
   ```bash
   python -m uvicorn app:app --reload
   ```
   Backend will run on http://127.0.0.1:8000

2. **Start the frontend** (in a new terminal):
   ```bash
   npm start
   ```
   Frontend will run on http://localhost:3000

3. **Access the application**:
   - Open http://localhost:3000 in your browser
   - Click "🔗 Manage Integrations" to test connections
   - Try SQLite queries immediately (no setup required)

## 📊 Features & Usage

### Database Operations
- **Immediate Use**: SQLite works out-of-the-box
- **Query Interface**: Execute SQL directly from the UI
- **Schema Discovery**: Automatic table and column inspection
- **Security**: Query validation prevents SQL injection

Example query:
```sql
SELECT COUNT(*) as total_customers, 
       AVG(order_value) as avg_order 
FROM customers 
WHERE created_date >= '2024-01-01'
```

### CRM Integration
- **Salesforce**: Retrieve contacts, create leads with validation
- **HubSpot**: Manage contacts with search and filtering
- **Zendesk**: Create and manage support tickets

### Data Analysis
- **File Upload**: Drag & drop Excel, CSV, Word documents
- **Visualizations**: Automatic chart generation
- **Smart Summaries**: AI-powered insights and statistics
- **Email Reports**: Rich, formatted email with analysis results

### Plan Management
- **Structured Plans**: See exactly what will be executed
- **Human Approval**: Pause for review before sensitive operations
- **Execution History**: Full audit trail with timestamps
- **Rollback**: Undo operations with state restoration

## 🔧 Configuration

### Database Connections
Configure in `.env` file (SQLite needs no configuration):

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# MySQL
MYSQL_HOST=localhost
MYSQL_DB=your_database
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

### CRM Authentication
Add your API credentials:

```env
# Salesforce
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_ACCESS_TOKEN=your_access_token

# HubSpot
HUBSPOT_API_KEY=your_api_key

# Zendesk
ZENDESK_SUBDOMAIN=your_subdomain
ZENDESK_EMAIL=your_email
ZENDESK_TOKEN=your_api_token
```

## 🛡️ Security Features

- **Query Validation**: SQL injection prevention
- **Parameter Binding**: Secure database queries
- **Just-in-Time Auth**: Credentials requested only when needed
- **Audit Logging**: Complete operation history
- **Access Control**: User-based permissions
- **State Encryption**: Secure state management via Portia

## 📚 API Documentation

When the backend is running, visit:
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

### Key Endpoints
- `GET /integrations/` - List available integrations
- `POST /database/query/` - Execute SQL queries
- `GET /crm/{type}/contacts/` - Retrieve CRM contacts
- `POST /run-plan/` - Execute AI plans with integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Portia AI](https://docs.portialabs.ai/)** - Core framework for transparent task automation
- **OpenAI** - GPT-4 language model for intelligent planning
- **FastAPI** - High-performance web framework
- **React** - Modern frontend development

## 🔗 Links

- **Portia AI Documentation**: https://docs.portialabs.ai/
- **Portia GitHub**: https://github.com/portialabs/portia
- **Project Repository**: [Add your GitHub URL here]
- **Live Demo**: [AI Workbench](https://youtu.be/GyqBx99XOrA)

## Contributors Involved
Users itself 😊, OpenAI, Perplexity AI, & Cursor

---

**Built with ❤️ using Portia AI for transparent, secure, and controllable task automation.**
