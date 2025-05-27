# PayLink MCP Server

**PayLink** is an open-source framework designed to streamline payment integration for developers building AI agents and financial applications across Africa.

Leveraging the **Model Context Protocol (MCP)**, PayLink exposes a unified interface that simplifies access to diverse payment providers—such as M-Pesa, Airtel Money seamless financial workflows without repetitive integration work.

## Why PayLink?

Africa’s financial ecosystem is fragmented. Developers often rebuild custom integrations for each payment provider, leading to redundancy and reduced scalability. **PayLink solves this** by:

- Providing **standardized MCP tools** for payments, invoicing, and reconciliation
- Empowering **AI agents** to handle payments intelligently
- Enabling **SMEs and micro-merchants** to access modern financial infrastructure
- Supporting **local-first** development with a global vision

---

## Currently Supported Providers

- **M-Pesa** (Safaricom) – Under active development  
  - STK Push API  
  - STK Push Status  
  - QR Code Generation  

---

## Available Tools

Each payment provider is exposed as a **tool** under the MCP server.

###  M-Pesa Tools

| Tool              | Description                              |
|-------------------|------------------------------------------|
| `stk_push`        | Initiates an STK Push request to a phone |
| `stk_push_status` | Checks the status of a previous STK push |
| `generate_qr_code`| Generates a payment QR code              |

More tools and enhancements are coming soon!

---

## Planned Features

- **Additional Mobile Money**: Airtel Money, T-Kash, MTN Mobile Money  
- **Banking Integrations**: PesaLink, Open Banking APIs  
- **Cross-Border Payments**: Integration with regional and international remittance platforms  
- **AI-Powered Payment Bots**: Enable AI agents to manage collections, invoicing, and reconciliation  

---

## Getting Started

This section guides you through setting up and running the PayLink MCP Server.

### Prerequisites

- **Docker**: Ensure you have Docker installed and running on your system. Docker is used to build and run the application in a containerized environment. You can download it from [docker.com](https://www.docker.com/get-started).

### Environment Variables

The application requires several environment variables for configuration, especially for connecting to the M-Pesa API and setting operational parameters.

1.  **Template**: A template for the environment variables is provided in `.env.example`.
2.  **Create `.env` file**: Copy the example file to a new `.env` file in the project root:
    ```bash
    cp .env.example .env
    ```
3.  **Edit `.env`**: Open the `.env` file and fill in the required values.

**Essential Variables:**

*   **M-Pesa API Credentials & Configuration**:
    *   `MPESA_CONSUMER_KEY`: Your M-Pesa application's consumer key.
    *   `MPESA_CONSUMER_SECRET`: Your M-Pesa application's consumer secret.
    *   `PASSKEY`: The M-Pesa passkey for your shortcode.
    *   `BUSINESS_SHORTCODE`: Your M-Pesa business shortcode (e.g., Paybill or Till Number).
    *   `CALLBACK_URL`: The publicly accessible URL that M-Pesa will use to send notifications (e.g., for STK push completion).
    *   `BASE_URL`: The base URL for the M-Pesa API (e.g., `https://sandbox.safaricom.co.ke` for sandbox, `https://api.safaricom.co.ke` for production).
*   **Server Configuration**:
    *   `TRANSPORT`: Specifies the communication protocol for the MCP server.
        *   `stdio`: For communication over standard input/output (typically used when the server is a child process of another application).
        *   `sse`: For communication over Server-Sent Events (HTTP-based).
    *   `APP_ENV`: Sets the application environment (e.g., "development", "production", "testing"). This affects logging and potentially other behaviors.

### Running with Docker

Once you have Docker installed and your `.env` file configured:

1.  **Copy `.env.example` to `.env`** (if you haven't already) and fill in your details:
    ```bash
    cp .env.example .env 
    # Then edit .env with your specific credentials and settings
    ```

2.  **Build the Docker image**:
    ```bash
    docker-compose build
    ```

3.  **Run the server**:
    ```bash
    docker-compose up
    ```
    This command will start the PayLink MCP server. If `TRANSPORT` is set to `stdio`, it will listen for MCP messages on stdin. If set to `sse`, it will start an HTTP server (default port 8050, check `docker-compose.yml` or server logs for the exact URL).

### Basic Usage / Available Tools

The PayLink MCP Server exposes payment functionalities as **MCP tools**. These tools can be called by any MCP-compliant client.

*   **Available M-Pesa Tools**: For a detailed list of currently available M-Pesa tools like `stk_push`, `stk_push_status`, and `generate_qr_code`, please refer to the [Available Tools](#available-tools) section in this README.

*   **Interacting with the Server**:
    *   **stdio**: If you are running the server with `TRANSPORT=stdio`, your parent application will communicate with it by sending JSON-RPC messages to its standard input and reading responses from its standard output. You can see an example of a Python client using this mode in `stdio_client.py`.
    *   **sse**: If using `TRANSPORT=sse`, you can interact with the server over HTTP using Server-Sent Events. The `sse_client.py` file provides an example of a Python client for this mode. Standard HTTP tools like `curl` can also be used to subscribe to the SSE stream and send commands via POST requests to specific endpoints (refer to MCP specification for details).

---

## Contributing

We're open to contributions! If you'd like to help support more payment providers or improve the MCP implementation:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

---

## License

MIT License — see [`LICENSE`](./LICENSE) for details.

---

## Contact

Feel free to reach out or open issues for support, ideas, or collaboration!

