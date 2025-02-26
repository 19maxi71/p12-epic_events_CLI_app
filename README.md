# Epic Events CRM

A secure CLI application for managing client relationships, contracts, and events.

## Setup

1. Clone the repository
```bash
git clone <repository-url>
cd epic-events-cli
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On macOS/Linux
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your:
# - SENTRY_DSN
# - DATABASE_URL (default: sqlite:///database.db)
# - ENVIRONMENT (development/production)
```

5. Initialize database:
```bash
python init_db.py
```

## Database Schema

- Users (id, full_name, email, password_hash, role_id)
- Roles (id, name)
- Clients (id, full_name, email, phone, company_name)
- Contracts (id, client_id, total_amount, amount_due, signed)
- Events (id, contract_id, support_contact, start_date, end_date, location, attendees)

## Usage

### Authentication
```bash
# Login (required before other operations)
python -m epic_events.cli login <email> <password>

# Logout
python -m epic_events.cli logout
```

### Client Operations
```bash
# List all clients
python -m epic_events.cli list-clients

# Add new client (Commercial/Admin only)
python -m epic_events.cli add-new-client
```

### Contract Operations
```bash
# List contracts
python -m epic_events.cli list-contracts

# Add contract (Commercial/Admin only)
python -m epic_events.cli add-new-contract
```

### Event Operations
```bash
# List events
python -m epic_events.cli list-events

# Filter events
python -m epic_events.cli filter-events --location "Paris"
```

## Error Tracking

Sentry integration monitors:
- All unexpected exceptions
- User creation/modification events
- Contract signature events
- Performance metrics

## Security Measures

- Environment variables for sensitive data
- Password hashing with bcrypt
- Role-based access control
- Session management
- No sensitive data in version control

## Development

1. Set up test data:
```bash
python seed_test_data.py
```

2. Default admin credentials:
```
Email: admin@email.com
Password: securepassword
```

## Project Structure

```
epic_events/
├── cli.py          # Command-line interface
├── config.py       # Configuration and Sentry setup
├── models.py       # Database models
├── crud.py         # Database operations
├── auth.py         # Authentication logic
└── utils.py        # Utility functions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License.