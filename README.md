# Flask Load Balancing

A Python Flask project demonstrating **Round Robin load balancing** across three instances of a Library Service. A Flask load balancer forwards incoming requests to the backend services and retries another instance if one is unavailable.

## Architecture

```text
                  Client
                    |
                    v
          Flask Load Balancer
               Port 8000
                    |
           Round Robin Routing
             /      |      \
            v       v       v
         Library Library Library
          5003    5004    5005
```

## Features

- Distributes requests across three backend instances.
- Returns the backend port in each response.
- Retries another backend when a request fails.
- Returns HTTP 503 when all backends are unavailable.
- Protects the shared routing index with a thread lock.

## Project Structure

```text
FlaskLoadBalancing/
├── library_instance.py
├── load_balancer.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3
- Flask
- Requests

## Installation

Clone the repository:

```bash
git clone https://github.com/itzsonu/FlaskLoadBalancing.git
cd FlaskLoadBalancing
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the Project

Open four terminals in the project folder. Keep all four processes running.

**Terminal 1 — Library instance on port 5003**

```bash
python library_instance.py 5003
```

**Terminal 2 — Library instance on port 5004**

```bash
python library_instance.py 5004
```

**Terminal 3 — Library instance on port 5005**

```bash
python library_instance.py 5005
```

**Terminal 4 — Load balancer on port 8000**

```bash
python load_balancer.py
```

## Testing Round Robin Routing

Open the following URL in a browser or send a GET request using Postman:

```text
http://127.0.0.1:8000/library
```

Example response:

```json
{
  "instance_port": 5003,
  "message": "Request handled successfully",
  "routed_via": "Flask Round Robin Balancer",
  "service": "Library Service"
}
```

Repeated requests should cycle through:

```text
5003 → 5004 → 5005 → 5003 → ...
```

To send nine sequential requests, run this in a fifth terminal:

```bash
python -c "import requests; [print('Request', i, '->', requests.get('http://127.0.0.1:8000/library', timeout=10).json()['instance_port']) for i in range(1,10)]"
```

With all backends running and no earlier requests since the load balancer started, the expected output is:

```text
Request 1 -> 5003
Request 2 -> 5004
Request 3 -> 5005
Request 4 -> 5003
Request 5 -> 5004
Request 6 -> 5005
Request 7 -> 5003
Request 8 -> 5004
Request 9 -> 5005
```

Earlier requests advance the cycle, so the first port may differ.

## Backend Health Endpoint

Each Library Service exposes a health endpoint. For example:

```text
http://127.0.0.1:5003/health
```

Example response:

```json
{
  "port": 5003,
  "status": "healthy"
}
```

## Fault Tolerance Testing

1. Press `Ctrl+C` in the terminal running port `5004`.
2. Continue sending requests to the load balancer.
3. Requests should succeed through ports `5003` and `5005`.
4. Restart the stopped instance:

   ```bash
   python library_instance.py 5004
   ```

5. Send more requests and confirm that port `5004` receives traffic again.

The load balancer retries backends during each request. It does not periodically poll `/health` or permanently remove failed instances. Failed attempts may add delay, and the remaining instances may receive uneven traffic.

## Testing Complete Backend Failure

Stop all three Library Service instances while keeping the load balancer running.

Send a request to:

```text
http://127.0.0.1:8000/library
```

Expected HTTP status:

```text
503 Service Unavailable
```

Expected response:

```json
{
  "error": "All Library Service instances unavailable"
}
```

## Expected Test Results

| Scenario | Expected behavior |
|---|---|
| All three backends running | Requests cycle through ports 5003, 5004, and 5005 |
| Port 5004 stopped | Requests succeed through the available instances |
| Port 5004 restarted | The restarted instance receives requests again |
| All backends stopped | The load balancer returns HTTP 503 |

## Technologies Used

- Python
- Flask
- Requests
- Python threading
