=========================================================
Some Notes For Django Projects
=========================================================

DEPLOYMENT
---------------------
- A basic click-through of the site works as expected (no broken images or links).
- Django logs are being written to file and/or being sent to a central aggregator.
- Monitoring/metrics platform is receiving data. Make sure you can see failures at every layer of the stack.
- Errors are being reported and triggering notifications.
- Third-party services are live and receiving data (payments, analytics, etc.)
- Outbound mail is flowing from your application servers and your Celery workers.
- Custom error (500 and 404) pages are setup at every level (load balancer, web accel- erator, Django).
- Django admin is not publicly available at /admin/.
- SSL certificate is valid and ciphers are secure 9 .
- Django-secure’s ```manage.py checksecure``` runs clean.

