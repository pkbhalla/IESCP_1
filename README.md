# IESCP (Influencer Engagement and Sponsorship Coordination Platform)

## Overview

IESCP is a platform designed to streamline the collaboration between sponsors and influencers. It allows sponsors to create and manage campaigns, send ad requests to influencers, and search for influencers. Influencers can view and accept/reject ad requests from sponsors, and they can also explore public campaigns and send ad requests to sponsors, initiating collaborations from their side.

## Features

### For Sponsors:
- **Dashboard:** Overview of ongoing campaigns and received ad requests from influencers.
- **Campaign Management:** Create and manage campaigns, track progress.
- **Ad Requests:** Send ad requests to influencers, accept/reject requests from influencers.
- **Influencer Search:** Search for influencers by niche, category, or name.

### For Influencers:
- **Dashboard:** Overview of ongoing campaigns where they are involved, pending ad requests.
- **Ad Requests:** Accept or reject requests from sponsors.
- **Campaign Search:** Search for public campaigns and send ad requests to sponsors.

### For Admin:
- **Dashboard:** View all users (sponsors, influencers) and their data.
- **Campaign Overview:** View and manage all ongoing campaigns.

## Technologies Used
- **Flask**: Python web framework for backend logic.
- **SQLAlchemy**: ORM for managing database relationships and queries.
- **Bootstrap**: Frontend framework for styling and responsive design.
- **SQLite**: Database for data persistence.
- **Jinja2**: Templating engine for rendering HTML with dynamic data.

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- Flask and other required dependencies (specified in `requirements.txt`)

### Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/pkbhalla/IESCP.git
   cd IESCP
   ```

2. **Install dependencies:**
   ```
    pip install -r requirements.txt
    ```
3. **Run the application:**
    ```
    python main.py
    ```
The app will be accessible at https://127.0.0.1:5000/. The database will be created automatically on first run.

## File Structure
```
IESCP/
│
├── static/
│   └── css/
│       └── style.css        # Custom styles
├── templates/                # HTML templates for rendering pages
├── main.py                   # Main application file
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
```
