# Epic Events CRM

A CLI application for managing client relationships, contracts, and events.

## Setup

1. Clone the repository
```bash
git clone <repository-url>
cd epic-events-cli
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Sentry DSN and other configurations
```

5. Initialize database
```bash
python init_db.py
```

## Usage

Basic commands:
```bash
# Login first
python -m epic_events.cli login <email> <password>

# Then you can use other commands
python -m epic_events.cli list-clients
python -m epic_events.cli list-contracts
python -m epic_events.cli list-events
```

See `python -m epic_events.cli --help` for all commands.

## Error Tracking

The application uses Sentry for:
- Unexpected exceptions
- User authentication attempts
- Contract signatures
- Performance monitoring

## Security

- All sensitive data is stored in `.env`
- Passwords are hashed
- Role-based access control
- Session management