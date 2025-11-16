# AXA Startup Evaluation: Topics & Use Cases

## Overview
This document defines the comprehensive taxonomy used to evaluate and categorize startups for AXA's venture client, innovation, and delivery projects. Startups are organized by **Topics** (strategic focus areas) and **Use Cases** (specific applications) aligned with AXA's priorities.

**Last Updated**: 2025-11-16  
**Total Use Cases**: 50+  
**Evaluation Framework**: Multi-dimensional scoring with provider assessment

---

## 📊 Topic Structure

Each startup is assigned to **ONE primary topic** based on its core value proposition, with one or more specific **use cases** within that topic.

### Primary Topics
1. **AI - Agentic**: Agentic platform enablers and infrastructure
2. **AI - Software Development**: Development tools and legacy modernization  
3. **AI - Claims**: Claims processing and automation solutions
4. **AI - Underwriting**: Underwriting automation and risk assessment
5. **AI - Contact Centers**: Customer support and engagement solutions
6. **Health**: Health innovations applicable to insurance
7. **Growth**: Sales, marketing, and business development solutions
8. **Responsibility**: Compliance, regulatory, and fraud detection
9. **Insurance Disruptor**: Policy administration and distribution innovation
10. **DeepTech**: Advanced technologies and R&D innovations
11. **Other**: Non-categorized or multi-domain solutions

---

## 🎯 Topic 1: AI - Agentic

**Strategic Purpose**: Build AXA's global agentic platform with foundational technologies and tools that internal teams can use to create autonomous AI systems.

**Key Principle**: These are **infrastructure/platform solutions**, not end-user products. They enable AXA to build, monitor, and operate its own agentic systems.

**Mapping**: Previously "Rule 1 - Agentic Platform Enablers"

### Use Case 1.1: Observability & Monitoring (F1.1)
**Description**: Tools for monitoring, tracing, and debugging **AI agents and LLM applications** specifically.

**CRITICAL**: This is ONLY for monitoring AI/ML/Agent systems, NOT for monitoring physical assets, infrastructure, or business operations.

**Capabilities**:
- Agent performance monitoring
- LLM request/response tracing  
- Cost tracking and optimization
- Error detection and alerting
- Production AI observability

**✅ Include**: LangSmith (monitors LLM agents), Arize AI (ML model monitoring), Helicone (LLM observability), AgentOps (agent monitoring)

**❌ Exclude**: 
- Physical asset monitoring (e.g., Constellr - satellite thermal imaging)
- Infrastructure monitoring (e.g., Datadog for servers, New Relic for applications)
- IoT device monitoring (e.g., sensor networks)
- Business/operations monitoring (e.g., dashboards, KPIs)
- Security monitoring (unless specific to AI/ML systems)

**Insurance Applications**:
- Monitor claims processing agents
- Track underwriting AI performance
- Debug customer service chatbots
- Optimize AI costs across departments

---

### Use Case 1.2: Agent Orchestration (F1.2)
**Description**: Platforms for coordinating multiple AI agents, managing agent-to-agent communication, and workflow orchestration.

**Capabilities**:
- Multi-agent coordination
- Agent communication protocols
- Workflow orchestration
- Task routing and delegation
- Agent lifecycle management

**Example Companies**: CrewAI, LangGraph, AutoGPT frameworks

**Insurance Applications**:
- Orchestrate claims processing workflows
- Coordinate underwriting decision agents
- Manage customer service agent teams
- Route tasks between specialized agents

---

### Use Case 1.3: LLM Operations (F1.3)
**Description**: Infrastructure for deploying, managing, and optimizing large language models in production.

**Capabilities**:
- Model deployment pipelines
- Prompt management and versioning
- Model performance optimization
- A/B testing frameworks
- Model governance

**Example Companies**: Humanloop, Vellum AI, Weights & Biases

**Insurance Applications**:
- Deploy custom insurance LLMs
- Manage prompt templates library
- Test model performance variations
- Ensure regulatory compliance

---

### Use Case 1.4: Agent Frameworks & SDKs (F1.4)
**Description**: Development frameworks and libraries for building AI agents.

**Capabilities**:
- Agent development frameworks
- Pre-built agent templates
- Integration libraries
- Tool calling infrastructure
- Memory management

**Example Companies**: LangChain, LlamaIndex, Semantic Kernel

**Insurance Applications**:
- Build custom claims agents
- Develop underwriting assistants
- Create policy Q&A agents
- Integrate with legacy systems

---

### Use Case 1.5: Data Infrastructure - Vector DBs & RAG (F1.5)
**Description**: Specialized databases and infrastructure for AI applications, including vector databases and RAG (Retrieval Augmented Generation) systems.

**Capabilities**:
- Vector similarity search
- Embedding management
- Document retrieval systems
- Knowledge base infrastructure
- Semantic search

**Example Companies**: Pinecone, Weaviate, Qdrant, Chroma

**Insurance Applications**:
- Store and retrieve policy documents
- Search claims history semantically
- Build knowledge bases for agents
- Enable accurate information retrieval

---

### Use Case 1.6: Agent Testing & Validation (F1.6)
**Description**: Tools for testing, validating, and ensuring quality of AI agents.

**Capabilities**:
- Agent behavior testing
- Output validation
- Safety testing
- Performance benchmarking
- Regression testing

**Example Companies**: Giskard, Kolena, Validmind

**Insurance Applications**:
- Validate underwriting decisions
- Test claims processing accuracy
- Ensure regulatory compliance
- Benchmark agent performance

---

## 🎯 Topic 2: AI - Software Development

**Strategic Purpose**: Agentic solutions for software development, testing, code migration, and integration with legacy systems—critical for AXA's digital transformation.

**Key Principle**: Must **accelerate development** or **modernize legacy systems**, not just generic dev tools.

**Mapping**: Previously "Rule 5 - Development & Legacy Modernization"

### Use Case 2.1: AI-Powered Code Development (F5.1)
**Description**: AI agents that assist with code generation, completion, and development.

**Capabilities**:
- Code generation
- Code completion
- Code review automation
- Architecture assistance
- Refactoring support

**Example Companies**: GitHub Copilot, Tabnine, Codeium, Cursor

**Insurance Applications**:
- Accelerate development
- Generate boilerplate code
- Assist junior developers
- Improve code quality

---

### Use Case 2.2: Automated Testing & QA (F5.2)
**Description**: AI agents for test generation, execution, and quality assurance automation.

**Capabilities**:
- Test generation
- Test execution
- Visual testing
- Bug detection
- Test maintenance

**Example Companies**: Testim, Mabl, Applitools, Functionize

**Insurance Applications**:
- Test policy systems
- Automate regression testing
- Ensure quality standards
- Reduce QA costs

---

### Use Case 2.3: Legacy Code Migration & Modernization (F5.3)
**Description**: Tools for migrating legacy code, modernizing mainframes, and language translation.

**Capabilities**:
- Code translation (e.g., COBOL to Java)
- Mainframe modernization
- Architecture transformation
- Cloud migration
- Technical debt reduction

**Example Companies**: Modern Systems, BluAge, Phase Change, Heirloom

**Insurance Applications**:
- Modernize policy systems
- Migrate mainframe code
- Reduce technical debt
- Enable cloud migration

---

### Use Case 2.4: Legacy System Integration & APIs (F5.4)
**Description**: Solutions for integrating legacy systems, generating APIs, and creating middleware.

**Capabilities**:
- API generation
- System integration
- Middleware platforms
- Data integration
- Legacy wrapping

**Example Companies**: MuleSoft, Boomi, SnapLogic, Jitterbit

**Insurance Applications**:
- Integrate policy systems
- Connect legacy platforms
- Enable API access
- Unify data sources

---

### Use Case 2.5: Code Intelligence & Documentation (F5.5)
**Description**: Tools for understanding codebases, generating documentation, and managing technical debt.

**Capabilities**:
- Code search
- Documentation generation
- Architecture visualization
- Dependency analysis
- Technical debt tracking

**Example Companies**: Sourcegraph, Swimm, Stepsize, Codacy

**Insurance Applications**:
- Understand legacy systems
- Document existing code
- Track technical debt
- Onboard developers

---

### Use Case 2.6: DevOps & CI/CD Automation (F5.6)
**Description**: Automation for deployment, infrastructure, and continuous delivery pipelines.

**Capabilities**:
- Deployment automation
- Infrastructure as code
- Pipeline optimization
- Release automation
- Incident response

**Example Companies**: Harness, CircleCI, GitLab, Spacelift

**Insurance Applications**:
- Automate deployments
- Reduce release cycles
- Improve reliability
- Enable DevOps practices

---

## 🎯 Topic 3: AI - Claims

**Strategic Purpose**: Targeted solutions specifically for insurance claims intake, assessment, settlement, and fraud detection.

**Key Principle**: Must be **insurance-specific** claims solutions, not generic document processing.

**Mapping**: Previously "Rule 3 - Insurance Solutions (Claims Category)"

### Use Case 3.1: Claims Processing & Automation (F3.1)
**Description**: Solutions specifically for insurance claims intake, assessment, and settlement.

**Capabilities**:
- FNOL automation
- Claims assessment
- Document extraction
- Settlement calculation
- Claims workflow management

**Example Companies**: Tractable, Shift Technology, Snapsheet, Cape Analytics

**Insurance Applications**:
- Automate auto claims
- Process property damage
- Detect claim fraud
- Accelerate settlements

---

### Use Case 3.2: Claims Fraud Detection (F3.7)
**Description**: Specialized fraud detection and prevention for insurance claims.

**Capabilities**:
- Claims fraud detection
- Network analysis
- Anomaly detection
- Investigation support
- Pattern recognition

**Example Companies**: Shift Technology, SAS Fraud Detection, Verisk fraud solutions

**Insurance Applications**:
- Detect fraudulent claims
- Identify fraud rings
- Reduce loss costs
- Prioritize investigations

---

## 🎯 Topic 4: AI - Underwriting

**Strategic Purpose**: AI for insurance underwriting, risk scoring, and pricing optimization.

**Key Principle**: Must be **insurance-specific** underwriting solutions, not generic risk assessment.

**Mapping**: Previously "Rule 3 - Insurance Solutions (Underwriting Category)"

### Use Case 4.1: Underwriting Automation & Risk Assessment (F3.2)
**Description**: AI for insurance underwriting, risk scoring, and pricing optimization.

**Capabilities**:
- Automated risk assessment
- Pricing optimization
- Document analysis
- Quote generation
- Risk modeling

**Example Companies**: Zelros, Gradient AI, Planck, Cytora

**Insurance Applications**:
- Automate small business underwriting
- Price policies accurately
- Assess risk faster
- Improve loss ratios

---

## 🎯 Topic 5: AI - Contact Centers

**Strategic Purpose**: AI agents and solutions for customer support, service automation, and policyholder engagement.

**Key Principle**: Focus on **customer-facing AI solutions** for support and engagement.

**Mapping**: Previously "Rule 2 - Service Providers (Customer Support)" + "Rule 3 - Customer Experience"

### Use Case 5.1: Customer Support Automation (F2.3 / F3.5)
**Description**: AI agents that handle customer inquiries, support tickets, and service requests.

**Capabilities**:
- Conversational AI
- Ticket routing and resolution
- Multi-channel support
- Knowledge base integration
- Sentiment analysis

**Example Companies**: Intercom, Ada, Ultimate.ai, Forethought, Pypestream

**Insurance Applications**:
- Answer policy questions
- Handle claims inquiries
- Route complex issues
- Provide 24/7 support

---

### Use Case 5.2: Digital Customer Experience (F3.5)
**Description**: Solutions for policyholder engagement, self-service, and digital experiences.

**Capabilities**:
- Self-service portals
- Mobile apps
- Digital onboarding
- Insurance chatbots
- Policyholder engagement

**Example Companies**: Boost.ai, Yellow.ai, Majesco CXP

**Insurance Applications**:
- Enable self-service
- Launch mobile apps
- Improve NPS scores
- Reduce call center volume

---

## 🎯 Topic 6: Health

**Strategic Purpose**: Health technology solutions applicable to health insurance, life insurance, wellness programs, and risk assessment.

**Key Principle**: Must have **clear insurance applicability**, not just general healthcare tech.

**Mapping**: Previously "Rule 4 - Health Innovations"

### Use Case 6.1: Health Data & Analytics (F4.1)
**Description**: Healthcare data platforms, predictive analytics, and population health insights.

**Capabilities**:
- Health risk prediction
- Medical claims analytics
- Population health management
- Outcome modeling
- Cost prediction

**Example Companies**: Komodo Health, Tempus, Lumiata, HealthVerity

**Insurance Applications**:
- Predict health risks
- Segment populations
- Optimize benefits design
- Reduce medical costs

---

### Use Case 6.2: Preventive Health & Wellness Programs (F4.2)
**Description**: Wellness platforms, chronic disease management, and preventive care solutions.

**Capabilities**:
- Wellness program delivery
- Chronic disease prevention
- Health coaching
- Behavior change programs
- Outcome tracking

**Example Companies**: Omada Health, Virta Health, Noom, Livongo

**Insurance Applications**:
- Reduce chronic disease costs
- Improve member health
- Lower claims frequency
- Enhance engagement

---

### Use Case 6.3: Remote Monitoring & Wearables (F4.3)
**Description**: Connected health devices, remote patient monitoring, and continuous health tracking.

**Capabilities**:
- Continuous monitoring
- Vital signs tracking
- Wearable data integration
- Alert systems
- Longitudinal health data

**Example Companies**: BioIntelliSense, Current Health, Biofourmis

**Insurance Applications**:
- Monitor chronic conditions
- Enable value-based care
- Detect health deterioration
- Reduce hospitalizations

---

### Use Case 6.4: Telemedicine & Virtual Care (F4.4)
**Description**: Virtual consultation platforms, digital therapeutics, and remote care delivery.

**Capabilities**:
- Virtual consultations
- Digital therapeutics
- Remote diagnosis
- E-prescribing
- Care coordination

**Example Companies**: Teladoc, MDLive, Doctor on Demand, 98point6

**Insurance Applications**:
- Reduce ER visits
- Provide accessible care
- Lower medical costs
- Improve member satisfaction

---

### Use Case 6.5: Mental Health & Behavioral Health (F4.6)
**Description**: Mental health platforms, therapy access, and behavioral health solutions.

**Capabilities**:
- Mental health benefits
- Therapy matching
- Digital mental health
- Crisis support
- Outcome tracking

**Example Companies**: Lyra Health, Spring Health, Ginger, Headspace Health

**Insurance Applications**:
- Provide mental health benefits
- Reduce disability claims
- Support employee wellness
- Lower healthcare costs

---

### Use Case 6.6: Healthcare Fraud Detection (F4.5)
**Description**: Fraud detection specific to medical claims, provider networks, and healthcare billing.

**Capabilities**:
- Medical claims fraud
- Provider fraud detection
- Billing anomaly detection
- Network integrity
- Healthcare compliance

**Example Companies**: Cotiviti, WhiteHat AI, LexisNexis Healthcare

**Insurance Applications**:
- Detect medical fraud
- Reduce improper payments
- Ensure provider integrity
- Combat healthcare waste

---

## 🎯 Topic 7: Growth

**Strategic Purpose**: Solutions for sales, marketing, lead generation, and business development.

**Key Principle**: Focus on **enterprise-ready solutions** with proven corporate traction.

**Mapping**: Previously "Rule 2 - Service Providers (Marketing & Sales Categories)"

### Use Case 7.1: Marketing Automation (F2.1)
**Description**: AI agents for marketing content creation, campaign management, and distribution.

**Capabilities**:
- Content generation agents
- Campaign automation
- Social media management
- SEO optimization
- Multi-channel distribution

**Example Companies**: Jasper AI, Copy.ai, Lately, Phrasee

**Insurance Applications**:
- Generate marketing content
- Automate email campaigns
- Create policy explainers
- Manage social media presence

---

### Use Case 7.2: Sales Enablement & Intelligence (F2.2)
**Description**: AI agents that support sales teams with intelligence, coaching, and automation.

**Capabilities**:
- Sales call analysis
- Lead scoring and prioritization
- Email assistance
- Sales coaching
- Pipeline intelligence

**Example Companies**: Gong, Chorus.ai, Lavender, People.ai

**Insurance Applications**:
- Analyze agent/broker calls
- Score insurance leads
- Coach sales representatives
- Optimize distribution channels

---

### Use Case 7.3: Data Analytics & Business Intelligence (F2.6)
**Description**: AI agents that analyze data, generate insights, and automate reporting.

**Capabilities**:
- Automated analytics
- Natural language querying
- Predictive modeling
- Report generation
- Data visualization

**Example Companies**: ThoughtSpot, Tableau (Einstein), Hex, Observable

**Insurance Applications**:
- Analyze claims patterns
- Generate risk reports
- Predict policy renewals
- Dashboard automation

---

## 🎯 Topic 8: Responsibility

**Strategic Purpose**: Compliance, regulatory reporting, fraud detection, and governance solutions.

**Key Principle**: Must address **regulatory requirements** or **fraud prevention** for insurance.

**Mapping**: Previously "Rule 3 - Compliance & Fraud Categories"

### Use Case 8.1: Compliance & Regulatory Solutions (F3.6)
**Description**: Insurance-specific compliance, regulatory reporting, and audit automation.

**Capabilities**:
- Regulatory reporting
- Compliance monitoring
- KYC/AML for insurance
- Audit automation
- Policy compliance

**Example Companies**: ComplyAdvantage, Trulioo, FIS regulatory solutions

**Insurance Applications**:
- Automate Solvency II reporting
- Monitor compliance
- Handle KYC processes
- Prepare for audits

---

### Use Case 8.2: Insurance Fraud Detection (F3.7)
**Description**: Specialized fraud detection and prevention for insurance claims and applications.

**Capabilities**:
- Application fraud prevention
- Claims fraud detection
- Network analysis
- Anomaly detection
- Investigation support

**Example Companies**: Shift Technology, SAS Fraud Detection, Verisk fraud solutions

**Insurance Applications**:
- Detect fraudulent claims
- Prevent application fraud
- Identify fraud rings
- Reduce loss costs

---

## 🎯 Topic 9: Insurance Disruptor

**Strategic Purpose**: Core insurance platform innovations for policy administration, distribution, and digital insurance.

**Key Principle**: Must be **transformative insurance technology**, not incremental improvements.

**Mapping**: Previously "Rule 3 - Policy Administration & Distribution Categories"

### Use Case 9.1: Policy Administration & Management (F3.3)
**Description**: Core systems for policy lifecycle management, issuance, and administration.

**Capabilities**:
- Policy issuance
- Renewals automation
- Endorsement processing
- Document generation
- Policy data management

**Example Companies**: Majesco, Duck Creek, EIS, Socotra

**Insurance Applications**:
- Modernize policy systems
- Automate renewals
- Handle mid-term changes
- Generate policy documents

---

### Use Case 9.2: Distribution & Agency Solutions (F3.4)
**Description**: Platforms for insurance distribution, agent/broker portals, and channel management.

**Capabilities**:
- Agent portals
- Quote and bind systems
- Commission management
- Producer management
- Digital distribution

**Example Companies**: Vertafore, Applied Systems, Accelerate

**Insurance Applications**:
- Empower agent networks
- Enable direct distribution
- Manage commissions
- Support brokers

---

## 🎯 Topic 10: DeepTech

**Strategic Purpose**: Advanced technologies, R&D innovations, and emerging tech with potential insurance applications.

**Key Principle**: Focus on **cutting-edge technology** with clear path to insurance value.

**Mapping**: New category for advanced/emerging technologies

### Use Case 10.1: Advanced AI & Machine Learning
**Description**: Novel AI techniques, advanced ML models, and research-driven innovations.

**Capabilities**:
- Novel AI architectures
- Advanced ML techniques
- Research innovations
- Experimental technologies

**Insurance Applications**:
- Risk modeling innovations
- Advanced predictive analytics
- Novel fraud detection methods

---

### Use Case 10.2: Emerging Technologies
**Description**: Blockchain, IoT, quantum computing, and other emerging technologies.

**Capabilities**:
- Blockchain applications
- IoT platforms
- Quantum computing
- Advanced sensors

**Insurance Applications**:
- Smart contracts
- Connected insurance
- Risk sensing
- Parametric insurance

---

## 🎯 Topic 11: Other

**Strategic Purpose**: Cross-functional solutions and multi-domain innovations that don't fit neatly into other topics.

**Key Principle**: Reserve for truly **cross-cutting solutions** or innovations spanning multiple topics.

### Use Case 11.1: Workflow Automation & RPA (F2.7)
**Description**: AI agents that automate business processes and workflows across systems.

**Capabilities**:
- Process automation
- Cross-system integration
- Document processing
- Task automation
- Workflow orchestration

**Example Companies**: UiPath, Automation Anywhere, Blue Prism, Workato

**Insurance Applications**:
- Automate policy issuance
- Process claims documents
- Update multiple systems
- Handle routine tasks

---

### Use Case 11.2: HR & Recruiting Automation (F2.4)
**Description**: AI agents for talent acquisition, candidate screening, and HR processes.

**Capabilities**:
- Resume screening
- Candidate matching
- Interview scheduling
- Onboarding automation
- HR query handling

**Example Companies**: HireVue, Phenom, Eightfold.ai, Pymetrics

**Insurance Applications**:
- Recruit actuaries and specialists
- Screen candidates efficiently
- Automate onboarding
- Manage internal transfers

---

### Use Case 11.3: Finance & Procurement Automation (F2.5)
**Description**: AI agents for financial processes, invoice management, and procurement.

**Capabilities**:
- Invoice processing
- Accounts payable automation
- Contract analysis
- Procurement automation
- Expense management

**Example Companies**: AppZen, Stampli, Coupa, Procurify

**Insurance Applications**:
- Process vendor invoices
- Automate claims payments
- Manage procurement
- Analyze contracts

---

## 📊 Scoring & Priority Framework

### Multi-Dimensional Scoring (0-100 points)

#### 1. Topic Match & Use Case Confidence (0-40 points)
- **Primary topic alignment**: 25-40 points (based on fit strength)
- **Use case specificity**: Bonus points for clear use case match
- **Multiple use cases within topic**: Small bonus for versatility

#### 2. Maturity & Stage Score (0-25 points)
Based on company maturity level:
- **Mature/Scaleup**: 25 points
- **Growth**: 20 points
- **Emerging**: 15 points
- **Early**: 10 points
- **Concept**: 5 points

#### 3. Funding Score (0-20 points)
Based on funding stage and amount:
- **Series C+**: 20 points
- **Series B**: 15 points
- **Series A**: 12 points
- **Seed**: 8 points
- **Pre-seed/Accelerator**: 5 points
- **Unfunded**: 2 points

#### 4. Innovation Score (0-10 points)
- **Breakthrough technology**: 10 points
- **Significant innovation**: 8 points
- **Incremental innovation**: 6 points
- **Standard solution**: 4 points

#### 5. Provider Usability (0-5 points)
- **Can use as provider**: 5 points
- **Potential provider**: 3 points
- **Cannot use as provider**: 0 points

### Priority Tiers

- **Tier 1 (Must Meet)**: 80-100 points
- **Tier 2 (High Priority)**: 60-79 points
- **Tier 3 (Medium Priority)**: 40-59 points
- **Tier 4 (Low Priority)**: 20-39 points
- **Excluded**: < 20 points

---

## 🔍 Provider Assessment Criteria

### Can Use as Provider ✓

A startup can be used as a provider if it meets these criteria:

1. **Solution-Ready**: Has a working product/service that AXA can procure and deploy
2. **Enterprise-Ready**: Supports enterprise requirements (security, compliance, scalability)
3. **Value Delivery**: Delivers clear business value to AXA entities
4. **Not a Competitor**: Is not an insurance carrier or direct competitor
5. **Operational**: Has operational capabilities to serve large enterprises

### Cannot Use as Provider ✗

A startup cannot be used as a provider if:

1. **Tool Only**: Only provides enabling technology that AXA must build on top of
2. **Competitor**: Is an insurance carrier or direct competitor
3. **Consumer-Only**: Only serves B2C with no enterprise offering
4. **Concept Stage**: No working product ready for deployment
5. **Wrong Market**: Serves markets not applicable to AXA

### Business Leverage Assessment

For each startup marked as usable provider, we assess:

1. **Primary Use Case**: How would AXA use this solution?
2. **Business Impact**: What problem does it solve for AXA?
3. **Value Creation**: What measurable value does it create?
4. **Integration Point**: Where in AXA's operations would it integrate?
5. **Strategic Fit**: How does it align with AXA's strategy?

---

## 📋 Topic Assignment Logic

### Single Primary Topic
Each startup is assigned to **ONE primary topic** based on its core value proposition:

- If a startup's main product is agent orchestration → **AI - Agentic**
- If a startup's main product is claims processing → **AI - Claims**
- If a startup's main product is underwriting AI → **AI - Underwriting**
- If a startup's main product is customer support AI → **AI - Contact Centers**
- If a startup's main product is code migration → **AI - Software Development**
- If a startup's main product is health analytics → **Health**
- If a startup's main product is marketing automation → **Growth**
- If a startup's main product is fraud detection → **Responsibility**
- If a startup's main product is policy administration → **Insurance Disruptor**

### Multiple Use Cases Within Topic
A startup can match multiple use cases **within the same topic**:

- Example: A health tech company might match both UC 6.1 (analytics) and UC 6.2 (wellness)
- Example: A dev tool might match both UC 2.1 (coding) and UC 2.2 (testing)

### Cross-Topic Exceptions
Only in rare cases should a startup match multiple topics:

- Must have genuinely distinct product lines serving different needs
- Each product line must be substantial and marketed separately
- Example: A company with both claims AI (AI - Claims) AND health analytics (Health)

---

## 🎯 Evaluation Best Practices

### For Insurance Domain Experts

1. **Think Provider-First**: Can AXA buy and use this, or is it just a tool/technology?
2. **Core Value Proposition**: What does this startup actually sell as their main product?
3. **Insurance Relevance**: Does this solve a real insurance problem?
4. **Regulatory Awareness**: Can this work in regulated insurance environment?
5. **Enterprise Readiness**: Is this ready for a company of AXA's scale?

### Common Pitfalls to Avoid

1. **Don't confuse technology used with product sold**
   - ❌ Wrong: "Uses LLM orchestration → AI - Agentic"
   - ✓ Right: "Sells orchestration platform → AI - Agentic" vs "Uses orchestration internally → Other topic"

2. **Don't assign multiple topics unless truly warranted**
   - ❌ Wrong: "Does marketing → Growth, Uses AI → AI - Agentic"
   - ✓ Right: "Sells marketing automation → Growth only"

3. **Don't mark competitors as providers**
   - ❌ Wrong: "Insurance carrier with great tech → Can use as provider"
   - ✓ Right: "Insurance carrier → Cannot use as provider (competitor)"

4. **Don't overestimate early-stage startups**
   - ❌ Wrong: "Cool idea → High score"
   - ✓ Right: "Cool idea but no product → Low score"

5. **Don't ignore insurance specificity**
   - ❌ Wrong: "Generic HR tool → Insurance relevant"
   - ✓ Right: "Generic HR tool → Not insurance-specific → Growth or Other if enterprise-ready"

6. **Focus on core product, not peripheral capabilities**
   - ❌ Wrong: "Marketing company that uses agents → AI - Agentic"
   - ✓ Right: "Marketing company that uses agents internally → Growth (their product is marketing)"

---

## 📚 Mapping: Old Rules to New Topics

For reference, here's how the previous "Rules" map to new "Topics":

| Old Framework | New Framework |
|--------------|---------------|
| Rule 1: Agentic Platform Enablers | **Topic: AI - Agentic** |
| Rule 2: Service Providers (Marketing/Sales) | **Topic: Growth** |
| Rule 2: Service Providers (Customer Support) | **Topic: AI - Contact Centers** |
| Rule 2: Service Providers (HR/Finance) | **Topic: Other** |
| Rule 2: Service Providers (Analytics) | **Topic: Growth** |
| Rule 2: Service Providers (Workflow/RPA) | **Topic: Other** |
| Rule 3: Insurance Solutions (Claims) | **Topic: AI - Claims** |
| Rule 3: Insurance Solutions (Underwriting) | **Topic: AI - Underwriting** |
| Rule 3: Insurance Solutions (Customer Experience) | **Topic: AI - Contact Centers** |
| Rule 3: Insurance Solutions (Policy Admin) | **Topic: Insurance Disruptor** |
| Rule 3: Insurance Solutions (Distribution) | **Topic: Insurance Disruptor** |
| Rule 3: Insurance Solutions (Compliance) | **Topic: Responsibility** |
| Rule 3: Insurance Solutions (Fraud) | **Topic: Responsibility** |
| Rule 4: Health Innovations | **Topic: Health** (all use cases) |
| Rule 5: Development & Legacy | **Topic: AI - Software Development** |

---

## 📋 Quick Reference: Use Case Codes

| Code | Use Case Name | Topic | Provider Type |
|------|--------------|-------|---------------|
| F1.1 | Observability & Monitoring | AI - Agentic | Platform |
| F1.2 | Agent Orchestration | AI - Agentic | Platform |
| F1.3 | LLM Operations | AI - Agentic | Platform |
| F1.4 | Agent Frameworks | AI - Agentic | Platform |
| F1.5 | Data Infrastructure | AI - Agentic | Platform |
| F1.6 | Agent Testing | AI - Agentic | Platform |
| F2.1 | Marketing Automation | Growth | Service |
| F2.2 | Sales Enablement | Growth | Service |
| F2.3 | Customer Support | AI - Contact Centers | Service |
| F2.4 | HR & Recruiting | Other | Service |
| F2.5 | Finance & Procurement | Other | Service |
| F2.6 | Data Analytics & BI | Growth | Service |
| F2.7 | Workflow Automation | Other | Service |
| F3.1 | Claims Processing | AI - Claims | Insurance |
| F3.2 | Underwriting Automation | AI - Underwriting | Insurance |
| F3.3 | Policy Administration | Insurance Disruptor | Insurance |
| F3.4 | Distribution & Agency | Insurance Disruptor | Insurance |
| F3.5 | Customer Experience | AI - Contact Centers | Insurance |
| F3.6 | Compliance & Regulatory | Responsibility | Insurance |
| F3.7 | Fraud Detection | Responsibility | Insurance |
| F4.1 | Health Data & Analytics | Health | Health |
| F4.2 | Preventive Health & Wellness | Health | Health |
| F4.3 | Remote Monitoring | Health | Health |
| F4.4 | Telemedicine | Health | Health |
| F4.5 | Healthcare Fraud | Health | Health |
| F4.6 | Mental Health | Health | Health |
| F5.1 | AI Code Development | AI - Software Development | Dev/Legacy |
| F5.2 | Automated Testing | AI - Software Development | Dev/Legacy |
| F5.3 | Legacy Migration | AI - Software Development | Dev/Legacy |
| F5.4 | System Integration | AI - Software Development | Dev/Legacy |
| F5.5 | Code Intelligence | AI - Software Development | Dev/Legacy |
| F5.6 | DevOps & CI/CD | AI - Software Development | Dev/Legacy |

---

**Document Version**: 3.0  
**Created**: 2025-11-16  
**Purpose**: AXA Startup Evaluation Topic & Use Case Taxonomy  
**Owner**: AXA Innovation Team  
**Status**: Active - Updated for SLUSH 2025 Evaluation with Topic-Based Structure
