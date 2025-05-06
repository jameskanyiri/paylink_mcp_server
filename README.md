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

Coming soon — setup instructions, environment configs, and example usage will be documented here.

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

