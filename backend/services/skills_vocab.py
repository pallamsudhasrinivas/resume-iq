SKILLS_VOCAB: set = {
    # ── Programming Languages ──────────────────────────────────────────────────
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
    "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Bash",
    "Shell", "PowerShell", "Groovy", "Lua", "Elixir", "Haskell", "Clojure",
    "F#", "Julia", "Dart", "COBOL", "Fortran", "SQL", "HTML", "CSS", "Sass",
    "Less", "Assembly", "Objective-C", "Visual Basic", "Tcl", "AWK", "Solidity",
    "Verilog", "VHDL", "Ada", "Prolog", "Erlang", "OCaml", "Scheme", "Racket",
    "Crystal", "Nim", "Zig",

    # ── Frontend Frameworks & Libraries ───────────────────────────────────────
    "React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "Gatsby",
    "Ember", "Backbone", "jQuery", "Bootstrap", "Tailwind", "Redux", "MobX",
    "Zustand", "Webpack", "Vite", "Rollup", "esbuild", "Babel", "Storybook",
    "Material UI", "Chakra UI", "Ant Design", "SvelteKit", "Remix", "Astro",
    "Alpine.js", "htmx", "Lit", "Solid.js", "Qwik", "Preact", "Mithril",
    "D3.js", "Three.js", "Highcharts", "Recharts", "Chart.js", "Framer Motion",

    # ── Backend Frameworks ─────────────────────────────────────────────────────
    "Django", "FastAPI", "Flask", "Spring Boot", "Spring", "Node.js", "Express",
    "Rails", "Laravel", "ASP.NET", ".NET", "NestJS", "Fastify", "Gin", "Echo",
    "Fiber", "Phoenix", "Sinatra", "Actix", "Quarkus", "Micronaut", "Play",
    "Ktor", "Hapi", "Strapi", "Sails.js", "AdonisJS", "Tornado", "Starlette",
    "Lumen", "Slim", "Symfony", "CakePHP", "CodeIgniter", "Grails", "Dropwizard",

    # ── Testing Frameworks & Tools ─────────────────────────────────────────────
    "JMeter", "LoadRunner", "Selenium", "Cypress", "pytest", "JUnit", "Gatling",
    "k6", "Postman", "TestNG", "Mocha", "Jest", "Jasmine", "RSpec", "Cucumber",
    "Playwright", "Appium", "Robot Framework", "SoapUI", "Insomnia", "Locust",
    "Artillery", "NUnit", "MSTest", "Chai", "Enzyme", "Testing Library",
    "Pact", "WireMock", "Mockito", "EasyMock", "PowerMock", "Karate",
    "BrowserStack", "Sauce Labs", "LambdaTest", "TestRail", "Allure",
    "Extent Reports", "Zephyr", "Xray", "qTest", "HP ALM", "Rational Quality Manager",
    "Tosca", "UFT", "ReadyAPI", "REST Assured", "Frisby", "Supertest",
    "SpecFlow", "xUnit", "Capybara", "Watir", "Geb",

    # ── Performance & Load Testing ─────────────────────────────────────────────
    "performance testing", "load testing", "stress testing", "spike testing",
    "soak testing", "endurance testing", "volume testing", "scalability testing",
    "test automation", "API testing", "NFR", "non-functional testing",

    # ── QA Practices ──────────────────────────────────────────────────────────
    "regression testing", "integration testing", "unit testing", "smoke testing",
    "sanity testing", "exploratory testing", "end-to-end testing",
    "functional testing", "security testing", "acceptance testing",
    "mobile testing", "cross-browser testing", "accessibility testing",
    "visual testing", "chaos engineering", "test strategy", "test planning",
    "test management", "defect management", "test coverage", "mutation testing",
    "contract testing", "synthetic monitoring", "shift-left testing",

    # ── Cloud Platforms ────────────────────────────────────────────────────────
    "AWS", "Azure", "GCP", "Google Cloud", "IBM Cloud", "Oracle Cloud",
    "DigitalOcean", "Linode", "Heroku", "Vercel", "Netlify",

    # ── AWS Services ──────────────────────────────────────────────────────────
    "S3", "EC2", "Lambda", "RDS", "DynamoDB", "CloudWatch", "EKS", "ECS",
    "Fargate", "SQS", "SNS", "API Gateway", "Cognito", "CloudFront", "Route 53",
    "CloudFormation", "CodePipeline", "CodeBuild", "CodeDeploy", "Glue",
    "Step Functions", "EventBridge", "AppSync", "Amplify", "Kinesis",
    "ElastiCache", "OpenSearch", "MSK", "EMR", "Athena", "Lake Formation",

    # ── Azure Services ─────────────────────────────────────────────────────────
    "Azure Functions", "Azure Kubernetes Service", "App Service",
    "Azure DevOps", "Azure Blob Storage", "Azure SQL", "Azure Cosmos DB",
    "Azure Event Hubs", "Azure Service Bus", "Azure Logic Apps",
    "Azure Active Directory", "Azure Monitor", "Azure Data Factory",

    # ── GCP Services ──────────────────────────────────────────────────────────
    "GKE", "Cloud Run", "Cloud Functions", "BigQuery", "Pub/Sub",
    "Cloud Spanner", "Firestore", "Cloud Composer", "Dataflow", "Vertex AI",
    "Cloud Build", "Cloud Armor",

    # ── DevOps & Infrastructure ────────────────────────────────────────────────
    "Docker", "Kubernetes", "Terraform", "Ansible", "Puppet", "Chef",
    "Jenkins", "GitHub Actions", "GitLab CI", "Travis CI", "CircleCI",
    "ArgoCD", "Helm", "Istio", "Prometheus", "Grafana", "Datadog",
    "New Relic", "PagerDuty", "Splunk", "Dynatrace", "Pulumi", "Vagrant",
    "Consul", "Vault", "Nexus", "Artifactory", "Harbor", "Tekton", "FluxCD",
    "OpenShift", "Rancher", "k3s", "Kustomize", "Packer", "Skaffold",
    "Buildkite", "Drone CI", "TeamCity", "Bamboo", "Spinnaker",
    "Zabbix", "Nagios", "CloudWatch", "Victoria Metrics", "Thanos",

    # ── Databases ─────────────────────────────────────────────────────────────
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
    "Neo4j", "InfluxDB", "Snowflake", "Redshift", "BigQuery", "SQLite",
    "Oracle", "SQL Server", "MariaDB", "ClickHouse", "Druid", "Cosmos DB",
    "CockroachDB", "TimescaleDB", "ArangoDB", "FaunaDB", "PlanetScale",
    "Citus", "YugabyteDB", "TiDB", "ScyllaDB", "Aerospike", "Couchbase",
    "RavenDB", "SurrealDB", "DuckDB", "Pinecone", "Weaviate", "Qdrant",
    "Milvus", "ChromaDB",

    # ── Message Brokers & Streaming ────────────────────────────────────────────
    "Apache Kafka", "RabbitMQ", "ActiveMQ", "Apache Pulsar", "NATS",
    "Celery", "ZeroMQ", "Amazon SQS", "Azure Service Bus",

    # ── Big Data & Data Engineering ────────────────────────────────────────────
    "Pandas", "NumPy", "Apache Spark", "Spark", "Kafka", "Airflow",
    "Apache Airflow", "dbt", "Tableau", "Power BI", "Hadoop", "Hive",
    "HBase", "ZooKeeper", "Databricks", "Flink", "Apache Flink", "Storm",
    "Apache Beam", "Prefect", "Luigi", "dask", "Polars", "PySpark",
    "Delta Lake", "Apache Iceberg", "Apache Hudi",

    # ── ML / AI ────────────────────────────────────────────────────────────────
    "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "OpenCV", "NLTK",
    "spaCy", "XGBoost", "LightGBM", "CatBoost", "Hugging Face", "MLflow",
    "Kubeflow", "Weights & Biases", "Ray", "ONNX", "LangChain", "LlamaIndex",
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "reinforcement learning", "feature engineering",
    "transfer learning", "AutoML", "model deployment", "model monitoring",
    "data labeling", "prompt engineering",

    # ── Data Visualization & BI ────────────────────────────────────────────────
    "Tableau", "Looker", "Metabase", "Apache Superset", "Grafana", "Kibana",
    "Power BI", "Qlik", "MicroStrategy", "SciPy", "Matplotlib", "Seaborn",
    "Plotly", "Bokeh", "Altair", "ggplot",

    # ── Search ────────────────────────────────────────────────────────────────
    "Elasticsearch", "Solr", "OpenSearch", "Algolia", "MeiliSearch",
    "Typesense",

    # ── API & Networking ──────────────────────────────────────────────────────
    "REST", "GraphQL", "gRPC", "WebSocket", "MQTT", "AMQP", "HTTP",
    "HTTPS", "OpenAPI", "Swagger", "Nginx", "Apache", "HAProxy", "Traefik",
    "TCP/IP", "DNS", "CDN", "WebRTC", "Protocol Buffers", "Avro",
    "JSON", "XML", "YAML", "Parquet",

    # ── Security ──────────────────────────────────────────────────────────────
    "OWASP", "SAST", "DAST", "penetration testing", "vulnerability assessment",
    "OAuth", "JWT", "SAML", "SSL", "TLS", "zero trust", "IAM",
    "cryptography", "PKI", "MFA", "SSO", "RBAC", "ABAC", "DevSecOps",
    "threat modeling", "security audit", "compliance", "SOC 2", "ISO 27001",
    "PCI DSS", "GDPR", "HIPAA", "NIST", "CIS",

    # ── Identity & Access ─────────────────────────────────────────────────────
    "OAuth2", "OpenID Connect", "Keycloak", "Auth0", "LDAP",
    "Active Directory", "Okta", "Ping Identity",

    # ── Mobile ────────────────────────────────────────────────────────────────
    "React Native", "Flutter", "iOS", "Android", "Xamarin", "Ionic",
    "SwiftUI", "Jetpack Compose", "Kotlin Multiplatform", "Cordova",
    "Capacitor", "NativeScript",

    # ── Build & Package Tools ─────────────────────────────────────────────────
    "Maven", "Gradle", "npm", "yarn", "pnpm", "Make", "CMake", "Bazel",
    "Ant", "SBT", "Cargo", "pip", "Poetry", "Conda",

    # ── Code Quality ──────────────────────────────────────────────────────────
    "SonarQube", "ESLint", "Prettier", "Black", "Flake8", "mypy", "pylint",
    "Rubocop", "Checkstyle", "PMD", "SpotBugs", "Codecov", "Coveralls",

    # ── Version Control & Collaboration ───────────────────────────────────────
    "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Mercurial",
    "JIRA", "Confluence", "Trello", "Asana", "Notion", "Linear",
    "Slack", "Monday.com",

    # ── OS & Platforms ────────────────────────────────────────────────────────
    "Linux", "Unix", "Windows", "macOS", "Ubuntu", "CentOS", "RHEL",
    "Alpine", "Debian",

    # ── IDE & Editors ─────────────────────────────────────────────────────────
    "IntelliJ", "PyCharm", "Eclipse", "Visual Studio", "VS Code", "Vim",
    "Neovim", "Xcode", "Android Studio",

    # ── API Management ────────────────────────────────────────────────────────
    "Kong", "Apigee", "MuleSoft", "WSO2", "Tyk",

    # ── Design & Prototyping ──────────────────────────────────────────────────
    "Figma", "Sketch", "Adobe XD", "InVision", "Zeplin",

    # ── Observability ─────────────────────────────────────────────────────────
    "OpenTelemetry", "Jaeger", "Zipkin", "Tempo", "Loki", "Fluentd",
    "Logstash", "Filebeat", "ELK Stack", "EFK Stack",

    # ── Feature Flags & Experimentation ───────────────────────────────────────
    "LaunchDarkly", "Unleash", "Flagsmith", "Optimizely",

    # ── Game & Graphics ───────────────────────────────────────────────────────
    "Unity", "Unreal Engine", "OpenGL", "DirectX", "Vulkan", "Metal",

    # ── Serverless & Edge ─────────────────────────────────────────────────────
    "Cloudflare Workers", "AWS Lambda", "Azure Functions",
    "Google Cloud Functions", "Deno Deploy",

    # ── CMS & E-Commerce ──────────────────────────────────────────────────────
    "WordPress", "Shopify", "Drupal", "WooCommerce", "Magento", "Contentful",
    "Sanity", "Strapi",

    # ── CRM / ERP ─────────────────────────────────────────────────────────────
    "Salesforce", "SAP", "HubSpot", "Zendesk", "ServiceNow",

    # ── Analytics ─────────────────────────────────────────────────────────────
    "Google Analytics", "Mixpanel", "Amplitude", "Segment", "Heap",
    "FullStory", "Hotjar",

    # ── Architecture Patterns ─────────────────────────────────────────────────
    "microservices", "serverless", "event-driven", "domain-driven design",
    "CQRS", "event sourcing", "clean architecture", "hexagonal architecture",
    "distributed systems", "message queue", "service mesh", "API gateway",
    "load balancing", "caching", "observability", "monitoring", "alerting",
    "tracing", "logging", "high availability", "fault tolerance",
    "circuit breaker", "saga pattern", "strangler fig",

    # ── Software Practices ────────────────────────────────────────────────────
    "TDD", "BDD", "DDD", "pair programming", "code review",
    "technical writing", "documentation", "CI/CD", "DevOps", "SRE",
    "GitOps", "MLOps", "DataOps", "FinOps", "infrastructure as code",
    "continuous integration", "continuous delivery", "continuous deployment",
    "trunk-based development", "feature flags", "A/B testing",
    "canary deployment", "blue-green deployment", "chaos engineering",

    # ── Soft Skills ───────────────────────────────────────────────────────────
    "leadership", "communication", "agile", "scrum", "kanban", "mentoring",
    "collaboration", "problem solving", "critical thinking", "teamwork",
    "project management", "time management", "adaptability", "creativity",
    "stakeholder management", "cross-functional", "technical leadership",
    "system design", "architecture review",

    # ── Blockchain & Web3 ─────────────────────────────────────────────────────
    "Ethereum", "blockchain", "smart contracts", "Web3", "DeFi", "NFT",
    "Solidity", "Hardhat", "Foundry", "IPFS",

    # ── Embedded & IoT ────────────────────────────────────────────────────────
    "embedded systems", "RTOS", "Arduino", "Raspberry Pi", "FPGA",
    "IoT", "ROS", "FreeRTOS", "Zephyr",
}
