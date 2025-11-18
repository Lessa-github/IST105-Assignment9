IST105 - Assignment 9: Django & Cisco DNA
This is the project for Assignment 9, which uses Django to connect to the Cisco DNA Center API and logs all activity to a remote MongoDB database. The entire architecture is deployed across two separate AWS EC2 instances for enhanced security.

1. Architecture & Security Groups 🛡️
The project utilizes a 2-tier architecture with strict Security Groups (SGs) to protect the database layer.

1. WebServer-A9-SG (The Web Server)
This group controls access to the Django application server:

Port 22 (SSH): Open to My IP (for administrator access).

Port 8000 (Django): Open to Anywhere (0.0.0.0/0) for public viewing.

2. MongoDB-A9-SG (The Database Server)
This is the highly restricted layer protecting MongoDB.

Port 22 (SSH): Open to My IP (for administrator access).

Port 27017 (MongoDB): This port has two critical rules:

Source WebServer-A9-SG: Allows the Django app to communicate with the database over the Private IP (fast and secure production link).

Source My IP: Allows your local development machine (WSL) to connect for the initial migrate and local testing.

2. Server Setup Instructions (Amazon Linux EC2)
Instructions for deploying the project on a fresh Amazon Linux EC2 instance:

1. Install System Packages
Bash

sudo yum update -y
sudo yum install git python3 python3-pip -y
2. Clone Repository & Install Dependencies
Bash

# Clone the repository
git clone https://github.com/Lessa-github/IST105-Assignment9.git
cd IST105-Assignment9

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Configure Project Secrets
The credentials file must be created manually (as it is excluded by .gitignore):

Bash

nano dna_center_cisco/dnac_config.py
Paste the public sandbox credentials:

Python

# Cisco DNA Center Sandbox Credentials
DNAC_URL = "https://sandboxdnac.cisco.com"
DNAC_USER = "devnetuser"
DNAC_PASS = "Cisco123!"
4. Configure Production Settings (settings.py)
Edit settings.py to use the server's specific production IPs:

Bash

nano assignment9/settings.py
ALLOWED_HOSTS: Set to your WebServer's Public IP: ALLOWED_HOSTS = ['<YOUR_WEBSERVER_PUBLIC_IP>']

DATABASES: Change the 'host' to your MongoDB's Private IP: 'host': '<YOUR_MONGODB_PRIVATE_IP>'

3. Running the Application 🚀
Bash

# Apply migrations (creates the 'api_logs' collection in Mongo)
python3 manage.py migrate

# Run the server
python3 manage.py runserver 0.0.0.0:8000
The application is now accessible at http://<YOUR_WEBSERVER_PUBLIC_IP>:8000.
