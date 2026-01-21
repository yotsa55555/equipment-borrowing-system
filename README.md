Equipment Booking System (Django on AWS)
managing equipment inventory and track borrowing/returning statuses. The system is deployed on AWS (Amazon Web Services) to ensure 24/7 availability.

🌐 Live Demo & Preview
-Live Link: http://52.221.109.70 

-Project Status: Production

[![Watch the Demo]](https://www.youtube.com/watch?v=lxVxRVy9sRs)

🏗️ System Architecture
-Architecture: Monolithic Django application served via Gunicorn.

-Deployment: Hosted on an Ubuntu Instance within AWS EC2.

-Server Stack: Nginx acts as a reverse proxy, handling incoming HTTP requests on port 80/443 and serving static files.

🛠️ Key Features
-Full CRUD Functionality: Admin can manage equipment entries, including descriptions, categories, and images.

-Borrowing/Return Logic: Real-time status updates (e.g., 'Available' to 'Borrowed') when a booking is confirmed.

-Inventory Tracking: Dashboard view for both users and admins to monitor the current status of all assets.

-User Authentication: Secure login and registration system.