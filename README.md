# AnchorCD

AnchorCD is an automated Continuous Deployment (CD) platform designed to simplify and streamline Docker-based infrastructure management.  
It focuses on Git-driven workflows and automated updates to keep your services anchored and up to date.

---

## Features (Planned)

- **Docker Compose Deployment**  
  Deploy and manage services directly from a `docker-compose.yml`.

- **Update Notifications**  
  Receive notifications through webhooks whenever an update or deployment occurs.

- **Image Update Checking**  
  Automatically check for new versions of Docker images used in your stacks.

- **Git-Defined Infrastructure**  
  Define and load your Docker infrastructure through Git repositories, keeping infrastructure declarative and version-controlled.

- **Automated Git Pull Requests**  
  AnchorCD can propose pull requests to update image versions or inform you of new available versions, ensuring you stay in control.

---

## Project Status

🚧 **Work in Progress** – Development started on *September 10, 2025*.  
Core features are under active development.

---

## Getting Started (future)

Instructions will follow once the first prototype is ready. Planned usage:

1. Clone this repository
2. Configure your `docker-compose.yml` and Git repo
3. Run AnchorCD to manage deployment and updates

---

## Roadmap

- [ ] Initial CLI / service scaffolding  
- [ ] Docker Compose deployment  
- [ ] Webhook notification system  
- [ ] Docker image update checker  
- [ ] Git integration (pull + PR automation)  
- [ ] First stable release  

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your suggestions and improvements.

---

## License

GNU AFFERO GENERAL PUBLIC LICENSE © 2025
