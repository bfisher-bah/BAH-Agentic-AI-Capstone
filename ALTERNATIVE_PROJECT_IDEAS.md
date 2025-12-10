# Alternative Capstone Project Ideas

These alternatives use the **same technical architecture** as the BeanBotics example (ticket classification agent with REST API, RAG, and optional WebSocket) but apply it to different business domains that may be more compelling or relevant.

---

## Quick Comparison

| Alternative | Industry | Appeal | Complexity |
|------------|----------|--------|------------|
| IT Help Desk | Technology | Universal relevance | Same |
| E-commerce Returns | Retail | High business impact | Same |
| HR Service Desk | Enterprise | Internal tool focus | Same |
| Property Maintenance | Real Estate | Tangible outcomes | Same |
| SaaS Support Portal | Software | Technical audience | Same |
| Municipal Services | Government | Public sector appeal | Same |

---

## Alternative 1: IT Help Desk Agent

### Business Context
An internal IT support system for a mid-size company. Employees submit tickets for technical issues, and the agent triages and routes them automatically.

### Why It's Compelling
- **Universal relevance** - Every company has IT support
- **Clear ROI story** - Reduces IT team workload by 40-60% on tier-1 tickets
- **Realistic escalation paths** - Easy to explain when human intervention is needed

### Classification Categories
| Category | Examples |
|----------|----------|
| Password/Access | Password resets, locked accounts, permission requests |
| Hardware | Laptop issues, monitor problems, keyboard/mouse |
| Software | Installation requests, crashes, license issues |
| Network/Connectivity | VPN problems, Wi-Fi issues, slow internet |
| Email/Communication | Outlook issues, Teams problems, calendar sync |
| Security | Suspicious emails, malware concerns, data breach |
| New Equipment | Hardware requests, upgrade requests |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Critical | Executive affected, security incident, entire team blocked |
| High | Employee cannot work, deadline mentioned |
| Medium | Inconvenience but workaround exists |
| Low | General questions, future requests |

### RAG Knowledge Base Content
- Password reset procedures
- VPN setup guides
- Common software troubleshooting
- Hardware replacement policies
- Security incident response steps

### Sample Tickets
```
Subject: Can't connect to VPN from home
Description: I've been trying to connect to the company VPN since this
morning but keep getting "connection timed out" error. I have an important
client presentation at 2pm and need access to the shared drive.
```

```
Subject: Need Photoshop installed
Description: Hi, I'm starting a new project next week that requires
Adobe Photoshop. Can someone help me get this installed? My employee
ID is EMP-4521.
```

---

## Alternative 2: E-commerce Customer Service Agent

### Business Context
A customer support system for an online retailer. Customers submit inquiries about orders, returns, and products.

### Why It's Compelling
- **High business impact** - Customer retention directly tied to support quality
- **Clear metrics** - Response time, resolution rate, customer satisfaction
- **Familiar to everyone** - Relatable use case for any audience

### Classification Categories
| Category | Examples |
|----------|----------|
| Order Status | Where's my order, tracking issues, delivery delays |
| Returns/Refunds | Return requests, refund status, exchange |
| Product Issues | Damaged item, wrong item, defective product |
| Payment/Billing | Charge disputes, payment failed, promo codes |
| Account Issues | Login problems, update address, delete account |
| Product Questions | Size guides, compatibility, availability |
| Complaints | Poor experience, escalation requests |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Urgent | Fraud suspected, large order value, repeat complaint |
| High | Order not received past delivery date, damaged item |
| Medium | General return request, account questions |
| Low | Product questions, feedback |

### RAG Knowledge Base Content
- Return policy (30-day window, conditions)
- Shipping timeframes by region
- Refund processing times
- Size and fit guides
- Warranty information

### Sample Tickets
```
Subject: Order never arrived - need refund
Description: I ordered a laptop bag (Order #ORD-98234) two weeks ago.
Tracking says delivered but I never received it. I've checked with
neighbors and my building's mailroom. This was a $89 purchase and I
need either a replacement or refund ASAP.
```

```
Subject: Wrong color received
Description: I ordered the blue version of your wireless headphones
but received black instead. How do I exchange this? Order number is
ORD-77891.
```

---

## Alternative 3: HR Service Desk Agent

### Business Context
An internal HR support system where employees submit questions about benefits, policies, and HR processes.

### Why It's Compelling
- **Enterprise focus** - Appeals to B2B/corporate audiences
- **Sensitive data handling** - Shows understanding of privacy concerns
- **Policy-driven** - Clear rules for classification and response

### Classification Categories
| Category | Examples |
|----------|----------|
| Time Off/Leave | PTO requests, sick leave, parental leave |
| Benefits | Health insurance, 401k, FSA questions |
| Payroll | Paycheck issues, tax forms, direct deposit |
| Onboarding | New hire questions, equipment, access |
| Performance | Review questions, promotion inquiries |
| Policy Questions | Dress code, remote work, expense reports |
| Complaints/Concerns | Workplace issues, harassment reports |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Critical | Harassment/safety concerns, payroll errors affecting pay |
| High | Benefits enrollment deadline, urgent leave request |
| Medium | General policy questions, benefits inquiries |
| Low | Future planning questions, general feedback |

### RAG Knowledge Base Content
- Employee handbook excerpts
- Benefits enrollment guides
- PTO policies
- Expense report procedures
- Remote work guidelines

### Sample Tickets
```
Subject: Health insurance for new baby
Description: My wife and I are expecting our first child in March.
What do I need to do to add the baby to my health insurance? Is there
a deadline after birth? Employee ID: HR-2847
```

```
Subject: Paycheck seems wrong
Description: My last paycheck was about $200 less than usual. I didn't
take any unpaid time off. Can someone look into this? I'm worried
there's an error with my tax withholding.
```

---

## Alternative 4: Property Management Maintenance Agent

### Business Context
A maintenance request system for a property management company handling multiple apartment buildings.

### Why It's Compelling
- **Tangible outcomes** - Physical repairs people can relate to
- **Clear urgency levels** - Water leak vs. squeaky door
- **Scheduling component** - Natural extension for follow-up

### Classification Categories
| Category | Examples |
|----------|----------|
| Plumbing | Leaks, clogged drains, toilet issues, water heater |
| Electrical | Outlets not working, lights out, breaker issues |
| HVAC | AC not cooling, heating problems, thermostat |
| Appliances | Refrigerator, stove, dishwasher, washer/dryer |
| Structural | Doors, windows, locks, flooring, walls |
| Pest Control | Insects, rodents, wildlife |
| Common Areas | Hallway lights, elevator, parking, trash |
| Safety/Emergency | Fire hazards, gas smell, flooding |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Emergency | Gas leak, flooding, no heat in winter, security breach |
| Urgent | No hot water, AC out in summer, toilet not working |
| Standard | Appliance issues, minor repairs |
| Low | Cosmetic issues, improvement requests |

### RAG Knowledge Base Content
- Emergency procedures
- Tenant responsibilities vs. landlord responsibilities
- Maintenance scheduling policies
- Appliance warranty information
- Building rules and regulations

### Sample Tickets
```
Subject: Water leaking from ceiling
Description: There's water dripping from my bathroom ceiling - I think
it's coming from the unit above me. It started about an hour ago and
is getting worse. I've put a bucket under it but I'm worried about
damage. Unit 4B, Building Oakwood.
```

```
Subject: Dishwasher won't drain
Description: My dishwasher hasn't been draining properly for the past
week. There's standing water at the bottom after each cycle. I've
tried cleaning the filter but it didn't help. Unit 12A.
```

---

## Alternative 5: SaaS Product Support Agent

### Business Context
Customer support for a B2B software product (e.g., project management tool, CRM, analytics platform).

### Why It's Compelling
- **Technical audience appeal** - Great for tech-focused presentations
- **Integration complexity** - Shows understanding of software ecosystems
- **Tiered support model** - Natural fit for escalation logic

### Classification Categories
| Category | Examples |
|----------|----------|
| Bug Report | Errors, crashes, unexpected behavior |
| Feature Request | New functionality, improvements |
| Integration | API issues, third-party connections, webhooks |
| Billing/Account | Subscription, invoices, plan changes |
| Performance | Slow loading, timeouts, sync delays |
| Security | Access issues, SSO problems, data concerns |
| How-To | Usage questions, best practices |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Critical | Production down, data loss, security vulnerability |
| High | Major feature broken, blocking business process |
| Medium | Bugs with workarounds, integration issues |
| Low | Feature requests, how-to questions |

### RAG Knowledge Base Content
- API documentation
- Integration guides
- Troubleshooting runbooks
- Feature release notes
- Security and compliance FAQs

### Sample Tickets
```
Subject: API returning 500 errors since yesterday
Description: Our integration with your API has been failing since
around 3pm yesterday. All POST requests to /api/v2/projects return
500 Internal Server Error. This is blocking our automated workflow.
Company: TechCorp, API Key prefix: tc_live_8x7...
```

```
Subject: Can we get bulk export to CSV?
Description: We need to export our project data to CSV for quarterly
reports. Currently we can only export one project at a time which is
very time-consuming with 200+ projects. Is there a bulk export feature
or API endpoint for this?
```

---

## Alternative 6: Municipal Services Agent

### Business Context
A citizen services portal for a city/town government handling resident inquiries and service requests.

### Why It's Compelling
- **Public sector relevance** - Appeals to government/civic tech audiences
- **Diverse request types** - Wide variety of categories
- **Community impact** - Tangible public benefit story

### Classification Categories
| Category | Examples |
|----------|----------|
| Utilities | Water, sewer, trash collection issues |
| Roads/Infrastructure | Potholes, streetlights, signs, sidewalks |
| Parks/Recreation | Park maintenance, facility reservations, programs |
| Permits/Licensing | Building permits, business licenses, parking permits |
| Public Safety | Non-emergency concerns, noise complaints |
| Code Enforcement | Property violations, zoning questions |
| General Information | Office hours, contact info, procedures |

### Priority Mapping
| Priority | Indicators |
|----------|------------|
| Urgent | Safety hazard, utility outage, accessibility blocked |
| High | Service disruption, time-sensitive permit |
| Standard | General requests, information inquiries |
| Low | Suggestions, non-urgent feedback |

### RAG Knowledge Base Content
- Permit application procedures
- Utility service information
- Parks and recreation schedules
- Code and zoning regulations
- Contact directory

### Sample Tickets
```
Subject: Large pothole on Main Street
Description: There's a dangerous pothole on Main Street near the
intersection with Oak Avenue. It's about 2 feet wide and several
inches deep. I saw a car hit it yesterday and damage their tire.
This needs to be fixed before someone gets hurt.
```

```
Subject: How do I get a permit for a backyard deck?
Description: I want to build a deck in my backyard this summer.
What permits do I need and what's the process? My property is at
123 Maple Drive. The deck would be about 12x16 feet.
```

---

## Implementation Notes

### What Stays the Same (Technical Architecture)

All alternatives use the identical technical stack:

1. **REST API Integration** - Same OpenAPI agent pattern
2. **LangChain/LangGraph** - Same state machine workflow
3. **Classification Engine** - Same LLM-based categorization (just different categories)
4. **Priority Assignment** - Same logic pattern (different rules)
5. **RAG System** - Same vector store approach (different documents)
6. **WebSocket** (optional) - Same real-time pattern
7. **Ticket Updates** - Same API interaction pattern

### What Changes (Content Only)

| Component | What to Modify |
|-----------|----------------|
| Classification prompt | Update category names and descriptions |
| Priority prompt | Update urgency indicators |
| RAG documents | Replace with domain-specific knowledge base |
| Sample tickets | Create new test data for the domain |
| Presentation | Update business context and value proposition |

### Effort Estimate

Switching to an alternative domain requires:

- **~2-4 hours**: Writing new classification/priority prompts
- **~2-4 hours**: Creating RAG knowledge base documents (5-7 markdown files)
- **~1-2 hours**: Creating sample tickets for testing
- **~1 hour**: Updating presentation context

**Total additional effort: ~6-11 hours** (minimal compared to core development)

---

## Recommendation

If your team wants to stand out while keeping complexity manageable:

### Best for Business Impact Story
**E-commerce Customer Service** - Everyone understands online shopping, and you can easily quantify ROI (faster response times, reduced support costs, improved customer satisfaction).

### Best for Technical Audience
**SaaS Product Support** - Shows understanding of software products, APIs, and technical troubleshooting. Great if presenting to a tech-focused group.

### Best for Universal Relevance
**IT Help Desk** - Every organization has IT support needs. Easy to explain and relatable to any audience.

### Best for Public Sector/Government Focus
**Municipal Services** - Strong civic impact story, diverse request types, and clear public benefit narrative.

---

## Discussion Questions for Team

1. Does our audience (evaluators/stakeholders) have a particular industry focus we should align with?

2. Do we have domain expertise in any of these areas that would make the project more authentic?

3. Which alternative would generate the most interesting demo scenarios?

4. Are we comfortable writing 5-7 knowledge base documents for a new domain?

5. Should we stick with BeanBotics (known quantity) or take a small risk for differentiation?

---

## Quick Decision Matrix

| If You Want... | Choose... |
|----------------|-----------|
| Lowest risk, fastest completion | BeanBotics (original) |
| Broad audience appeal | IT Help Desk or E-commerce |
| Enterprise/B2B focus | HR Service Desk or SaaS Support |
| Tangible/physical outcomes | Property Maintenance |
| Public sector/civic angle | Municipal Services |

---

*Remember: The technical implementation is identical regardless of which domain you choose. The differentiation is purely in the business context, prompts, and knowledge base content.*