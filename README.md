# sdn-architecture
/sdn-platform-root
│
├── /docs                    # Knowledge Base
│   ├── /architecture        # C4, system context
│   ├── /decisions           # ADRs (Why we chose X)
│   ├── /diagrams            # Mermaid sources
│   └── /manuals             # Operator guides
│
├── /schemas                 # THE CONTRACTS (New!)
│   ├── /openapi             # API Specs for UI team
│   ├── /sql                 # DB Schemas
│   └── /yang                # Network Models
│
├── /odl-controller          # The Engine
│   ├── /karaf-build         # pom.xml
│   ├── /config              # netconf.cfg, org.ops4j.pax.web.cfg
│   └── /custom-plugins      # Java logic (if needed)
│
├── /backend-services        # The Brains
│   ├── /common              # Shared code (Loggers, Auth Middleware)
│   ├── /inventory-svc       # Device Inventory
│   ├── /orchestrator-svc    # Logic & Translation
│   ├── /telemetry-svc       # Kafka -> InfluxDB
│   └── /auth-svc            # User Management
│
├── /ui-frontend             # The Face (React/Angular)
│
├── /infrastructure          # The Plumbing
│   ├── /docker              # Base images
│   ├── /k8s                 # Helm Charts
│   ├── /ci-cd               # Pipelines
│   └── /local-dev           # docker-compose.yml (Crucial!)
│
└── /tests                   # Quality Assurance
    └── /e2e                 # System Integration Tests
