# Smart Expense & Budget Manager — Project Specification

**Document:** `SPEC.md`  
**Version:** 1.0  
**Status:** Draft for Implementation  
**Development Method:** Spec-Driven Development (SDD)  
**Project Type:** Full-stack Web Application  
**Primary Goal:** Build, test, and deploy a reliable personal finance application for tracking income, expenses, budgets, and spending insights.

---

# 1. Project Overview

## 1.1 Problem Statement

Managing personal finances manually is difficult because users often:

- forget where money was spent,
- lack visibility into monthly spending,
- exceed category budgets,
- struggle to identify spending patterns,
- maintain financial information across multiple spreadsheets or applications.

The Smart Expense & Budget Manager will provide a centralized web application where a user can record income and expenses, define budgets, monitor financial activity, and understand spending patterns through dashboards and visualizations.

The application should prioritize:

1. simplicity,
2. correctness,
3. usability,
4. data consistency,
5. security,
6. meaningful financial insights.

---

# 2. Project Goals

## 2.1 Primary Goals

The application MUST allow an authenticated user to:

1. Register an account.
2. Log in and log out.
3. Create, edit, and delete income transactions.
4. Create, edit, and delete expense transactions.
5. Categorize transactions.
6. Define monthly budgets for expense categories.
7. View current-month financial summaries.
8. View spending by category.
9. Track budget utilization.
10. Filter and search transactions.
11. View historical financial information.
12. Receive budget warnings.
13. View charts and financial trends.
14. Deploy the application to a publicly accessible environment.

---

# 3. Non-Goals

The following features are explicitly OUT OF SCOPE for Version 1:

- Direct bank account integration.
- Credit-card API integration.
- Cryptocurrency tracking.
- Investment portfolio management.
- Tax calculation.
- Automatic bank transaction synchronization.
- Financial advice.
- Payment processing.
- Multi-currency conversion.
- Real-money transfers.
- Social sharing of financial information.

These features may be considered for future versions.

---

# 4. Target User

The primary user is an individual who wants to track personal finances.

The MVP assumes:

- one user manages their own financial data,
- each user has isolated data,
- transactions are manually entered,
- one primary currency is used,
- the user primarily manages monthly finances.

---

# 5. Core User Stories

## US-01: User Registration

**As a new user,**

I want to create an account,

so that I can securely manage my personal financial data.

### Acceptance Criteria

- User provides:
  - name
  - email
  - password
- Email must be valid.
- Email must be unique.
- Password must satisfy the password policy.
- Password must never be stored as plaintext.
- Successful registration creates a user account.
- User receives a successful registration response.
- Invalid registration data produces a meaningful error.

---

# 6. Authentication

## US-02: Login

A registered user MUST be able to log in using:

- email
- password

Successful authentication MUST establish an authenticated session.

The application MUST NOT expose passwords in API responses.

---

## US-03: Logout

The user MUST be able to log out.

After logout, protected endpoints MUST reject unauthenticated requests.

---

# 7. Transaction Management

Transactions are divided into two types:

```text
INCOME
EXPENSE
```

## 7.1 Transaction Fields

Every transaction MUST contain:

| Field | Type | Required |
|---|---|---|
| id | UUID | Yes |
| user_id | UUID | Yes |
| type | enum | Yes |
| amount | decimal | Yes |
| category_id | UUID | Yes |
| description | string | No |
| transaction_date | date | Yes |
| created_at | datetime | Yes |
| updated_at | datetime | Yes |

---

# 8. Income Transactions

The user MUST be able to:

- create income,
- edit income,
- delete income,
- view income.

Examples:

- salary
- freelance income
- bonus
- scholarship
- other income

---

# 9. Expense Transactions

The user MUST be able to:

- create expenses,
- edit expenses,
- delete expenses,
- view expenses.

Examples:

- food
- rent
- transport
- shopping
- entertainment
- utilities.

---

# 10. Categories

The application MUST support transaction categories.

Initial expense categories:

```text
Food
Housing
Transportation
Shopping
Entertainment
Healthcare
Education
Utilities
Travel
Subscriptions
Other
```

Initial income categories:

```text
Salary
Freelance
Business
Investment
Scholarship
Other
```

Categories should be represented in the database rather than hard-coded throughout the application.

---

# 11. Category Management

For Version 1, users MAY use predefined categories.

Custom category creation is optional.

If custom categories are implemented, users MUST be able to:

- create a category,
- rename a category,
- deactivate a category.

Deleting a category that has existing transactions SHOULD NOT physically delete historical transaction information.

Instead, the category should be marked inactive.

---

# 12. Transaction Validation

The backend MUST validate transaction data.

## Amount

- Must be greater than zero.
- Must use decimal-safe financial representation.
- Floating-point arithmetic MUST NOT be used for persisted monetary values.

Example:

```text
100.50
```

is valid.

```text
0
-100
```

are invalid.

## Description

- Optional.
- Maximum length: 255 characters.

## Date

- Must be a valid date.
- Future transaction dates MAY be allowed, but the behavior must be consistent throughout the application.

---

# 13. Dashboard

After login, the user SHOULD be presented with a financial dashboard.

The dashboard MUST contain:

### Summary Cards

```text
Total Income
Total Expenses
Current Balance
Savings Rate
```

Where:

```text
Balance = Total Income - Total Expenses
```

and:

```text
Savings Rate =
    (Income - Expenses) / Income × 100
```

If income is zero, savings rate should be displayed as:

```text
N/A
```

rather than causing a division-by-zero error.

---

# 14. Monthly Dashboard

The user MUST be able to select a month.

For the selected month, the system should calculate:

```text
Total income
Total expenses
Net balance
Savings rate
Top spending categories
Budget utilization
```

Default dashboard month:

```text
Current calendar month
```

---

# 15. Spending Breakdown

The dashboard MUST provide a category-level breakdown of expenses.

Example:

```text
Food             ₹8,000
Housing         ₹20,000
Transport        ₹4,000
Shopping         ₹6,000
Entertainment    ₹2,000
```

The UI SHOULD visualize this using a pie/donut chart.

---

# 16. Spending Trend

The application SHOULD display spending over time.

Minimum visualization:

```text
Month → Expense Amount
```

A line or bar chart may be used.

Example:

```text
Jan  ₹20k
Feb  ₹24k
Mar  ₹18k
Apr  ₹27k
```

---

# 17. Budget Management

Users MUST be able to define monthly budgets.

A budget consists of:

| Field | Type |
|---|---|
| id | UUID |
| user_id | UUID |
| category_id | UUID |
| month | YYYY-MM |
| amount | decimal |
| created_at | datetime |
| updated_at | datetime |

---

# 18. Budget Rules

A user MUST NOT have multiple active budgets for the same:

```text
user + category + month
```

Example:

```text
User: A
Category: Food
Month: August 2026
```

must correspond to at most one budget.

A database-level uniqueness constraint SHOULD enforce this.

---

# 19. Budget Utilization

For every budget:

```text
Spent = Sum(expenses in category during month)

Remaining = Budget - Spent

Utilization =
    Spent / Budget × 100
```

Example:

```text
Food Budget = ₹10,000
Food Spending = ₹7,500

Utilization = 75%

Remaining = ₹2,500
```

---

# 20. Budget Warning System

The application MUST identify budget thresholds.

Recommended thresholds:

```text
< 70%       Normal
70–89%      Warning
90–99%      Critical
>= 100%     Exceeded
```

The UI should clearly communicate the state.

Example:

```text
Food
₹7,500 / ₹10,000

75% used

⚠ Approaching budget
```

For an exceeded budget:

```text
Food
₹11,200 / ₹10,000

112% used

Budget exceeded by ₹1,200
```

---

# 21. Budget Alerts

The MVP MAY provide in-app alerts.

Example:

```text
⚠ Your Food budget has reached 90%.
```

The system SHOULD avoid generating duplicate alerts for the same threshold event.

Email/SMS/push notifications are OUT OF SCOPE for Version 1.

---

# 22. Transaction History

The user MUST have a transaction history page.

Each row SHOULD display:

```text
Date
Type
Category
Description
Amount
Actions
```

Example:

```text
25 Aug | Expense | Food | Dinner | ₹450 | Edit Delete
```

---

# 23. Filtering

Users MUST be able to filter transactions by:

- date range,
- transaction type,
- category.

Optional:

- amount range.

---

# 24. Searching

Users SHOULD be able to search transactions by description.

Example:

```text
Search: "Amazon"
```

returns transactions whose descriptions contain:

```text
Amazon
```

Search behavior should be case-insensitive.

---

# 25. Sorting

Transactions SHOULD support sorting by:

- newest first,
- oldest first,
- highest amount,
- lowest amount.

Default:

```text
Newest first
```

---

# 26. Pagination

The backend SHOULD support pagination for transaction lists.

Example API parameters:

```text
?page=1
&page_size=20
```

The backend MUST enforce a maximum page size.

Recommended:

```text
maximum = 100
```

---

# 27. Financial Calculations

All financial calculations MUST be performed on the backend.

The frontend may display calculated results but MUST NOT be considered the source of truth.

For example:

```text
Frontend:
display balance

Backend:
calculate balance
```

This prevents inconsistent calculations between clients.

---

# 28. Database Design

Recommended relational database:

```text
PostgreSQL
```

---

# 29. Core Database Tables

Minimum tables:

```text
users
categories
transactions
budgets
```

Optional:

```text
budget_alerts
refresh_tokens
audit_logs
```

---

# 30. Users Table

Suggested schema:

```text
users
-----
id
name
email
password_hash
created_at
updated_at
```

Constraints:

```text
id PRIMARY KEY
email UNIQUE NOT NULL
password_hash NOT NULL
```

---

# 31. Categories Table

```text
categories
----------
id
name
type
is_active
created_at
updated_at
```

Where:

```text
type ∈ {INCOME, EXPENSE}
```

---

# 32. Transactions Table

```text
transactions
------------
id
user_id
category_id
type
amount
description
transaction_date
created_at
updated_at
```

Relationships:

```text
users 1 ──── N transactions

categories 1 ──── N transactions
```

---

# 33. Budgets Table

```text
budgets
-------
id
user_id
category_id
month
amount
created_at
updated_at
```

Relationship:

```text
users 1 ──── N budgets

categories 1 ──── N budgets
```

---

# 34. Data Isolation

A user MUST ONLY be able to access their own:

- transactions,
- budgets,
- financial summaries,
- alerts.

Example:

```text
User A requests transaction belonging to User B
                ↓
             403/404
```

The backend MUST NOT rely on the frontend to enforce this restriction.

---

# 35. API Design

The backend SHOULD expose RESTful APIs.

Base URL:

```text
/api/v1
```

---

# 36. Authentication APIs

## Register

```http
POST /api/v1/auth/register
```

Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "StrongPassword123!"
}
```

---

## Login

```http
POST /api/v1/auth/login
```

---

## Logout

```http
POST /api/v1/auth/logout
```

---

# 37. Transaction APIs

```text
GET    /api/v1/transactions
POST   /api/v1/transactions
GET    /api/v1/transactions/{id}
PATCH  /api/v1/transactions/{id}
DELETE /api/v1/transactions/{id}
```

---

# 38. Budget APIs

```text
GET    /api/v1/budgets
POST   /api/v1/budgets
GET    /api/v1/budgets/{id}
PATCH  /api/v1/budgets/{id}
DELETE /api/v1/budgets/{id}
```

---

# 39. Dashboard APIs

```text
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/category-breakdown
GET /api/v1/dashboard/monthly-trend
GET /api/v1/dashboard/budget-status
```

Each endpoint MUST accept a month or date range where appropriate.

---

# 40. API Error Format

All API errors SHOULD follow a consistent structure.

Example:

```json
{
  "error": {
    "code": "INVALID_AMOUNT",
    "message": "Transaction amount must be greater than zero."
  }
}
```

Do not expose:

- database stack traces,
- passwords,
- secret keys,
- internal filesystem paths.

---

# 41. HTTP Status Codes

Recommended usage:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

---

# 42. Frontend Requirements

The frontend SHOULD contain:

```text
/login
/register
/dashboard
/transactions
/budgets
/settings
```

---

# 43. Dashboard UI

The dashboard should contain:

```text
------------------------------------------------
Smart Expense Manager

Income      Expenses      Balance      Savings
₹80,000     ₹42,000       ₹38,000       47.5%

------------------------------------------------

Spending by Category

        [Pie Chart]

------------------------------------------------

Monthly Spending Trend

        [Line Chart]

------------------------------------------------

Budget Status

Food          75%
Shopping      105%
Transport     40%

------------------------------------------------
```

---

# 44. Transaction UI

The user MUST be able to add a transaction using a form.

Fields:

```text
Transaction Type
Amount
Category
Description
Date
```

The form MUST display validation errors clearly.

---

# 45. Budget UI

The budget page SHOULD show:

```text
Category
Budget
Spent
Remaining
Utilization
Status
```

Example:

```text
Food
Budget: ₹10,000
Spent: ₹7,500
Remaining: ₹2,500
Usage: 75%
Status: Warning
```

---

# 46. Responsive Design

The application MUST work on:

- desktop,
- tablet,
- mobile.

The minimum supported screen width should be approximately:

```text
320px
```

---

# 47. Accessibility

The frontend SHOULD follow basic accessibility practices:

- semantic HTML,
- labels for form controls,
- keyboard navigation,
- sufficient contrast,
- meaningful error messages,
- accessible chart descriptions where practical.

---

# 48. Security Requirements

Passwords MUST be hashed using a secure password hashing algorithm.

Recommended:

```text
Argon2
```

or:

```text
bcrypt
```

Passwords MUST NEVER be logged.

Authentication tokens MUST be handled securely.

Secrets MUST be stored using environment variables.

Example:

```text
DATABASE_URL
SECRET_KEY
JWT_SECRET
```

These MUST NOT be committed to Git.

---

# 49. Authorization

Every protected endpoint MUST verify:

1. user is authenticated,
2. requested resource belongs to authenticated user.

The backend MUST enforce authorization.

---

# 50. Input Security

The backend MUST validate and sanitize user input.

The application MUST protect against:

- SQL injection,
- XSS,
- malformed requests,
- unauthorized resource access.

Parameterized queries or ORM mechanisms MUST be used.

---

# 51. Logging

The backend SHOULD maintain structured logs.

Logs SHOULD contain:

```text
timestamp
request method
endpoint
status code
request duration
```

Sensitive information MUST NOT be logged.

Do NOT log:

```text
password
authentication token
financial credentials
secret keys
```

---

# 52. Testing Strategy

Testing MUST be part of the project.

The application SHOULD contain:

```text
Unit Tests
Integration Tests
API Tests
Frontend Tests
End-to-End Tests
```

---

# 53. Unit Tests

At minimum test:

```text
balance calculation
savings rate calculation
budget utilization
budget threshold classification
transaction validation
```

Example:

```text
Income = ₹1000
Expense = ₹400

Balance = ₹600
```

---

# 54. Budget Calculation Tests

Example:

```text
Budget = ₹10,000
Spent = ₹7,500
```

Expected:

```text
Utilization = 75%
Remaining = ₹2,500
Status = WARNING
```

---

# 55. Edge Cases

The system MUST handle:

### Zero income

```text
Income = ₹0
Expense = ₹500
```

Savings rate:

```text
N/A
```

### Zero budget

A budget of zero SHOULD be rejected.

### Very large amount

The application should not overflow or produce invalid calculations.

### Empty transaction list

Dashboard should display:

```text
No transactions yet.
```

rather than an error.

### Deleted category

Historical transactions must remain valid.

### Unauthorized access

User A cannot retrieve User B's transaction.

---

# 56. Performance Requirements

For normal usage:

- API responses SHOULD generally be below 500 ms.
- Dashboard queries SHOULD be optimized.
- Database indexes SHOULD exist on commonly queried fields.

Recommended indexes:

```text
transactions.user_id
transactions.transaction_date
transactions.category_id
budgets.user_id
budgets.month
```

---

# 57. Technology Stack

The agent MAY use equivalent technologies, but the preferred stack is:

## Frontend

```text
Next.js / React
TypeScript
Tailwind CSS
Recharts
```

## Backend

Preferred:

```text
FastAPI
Python
Pydantic
SQLAlchemy
```

## Database

```text
PostgreSQL
```

## Authentication

```text
JWT or secure session-based authentication
```

## Deployment

Possible:

```text
Frontend → Vercel
Backend → Render/Railway/Fly.io
Database → Managed PostgreSQL
```

The exact deployment provider may be selected based on availability.

---

# 58. Repository Structure

Recommended:

```text
01_Smart_Expense_&_Budget_Manager/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── tests/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── core/
│   │
│   └── tests/
│
├── specs/
│
├── docker/
│
├── .env.example
├── README.md
└── SPEC.md
```

---

# 59. Architecture

The recommended architecture is:

```text
                    ┌──────────────┐
                    │    User      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Frontend   │
                    │ React/Next   │
                    └──────┬───────┘
                           │ REST API
                           ▼
                    ┌──────────────┐
                    │   Backend    │
                    │   FastAPI    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Auth Service  Transaction   Budget
                           Service     Service
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │ PostgreSQL   │
                    └──────────────┘
```

---

# 60. Backend Layering

The backend SHOULD use separation of concerns:

```text
API Layer
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database
```

### API Layer

Responsible for:

- HTTP requests,
- authentication,
- validation,
- HTTP responses.

### Service Layer

Responsible for:

- business logic,
- calculations,
- budget rules,
- authorization decisions.

### Repository Layer

Responsible for:

- database access,
- queries,
- persistence.

---

# 61. SDD Workflow

This project MUST be developed using Spec-Driven Development.

The development process is:

```text
Requirement
    ↓
Specification
    ↓
Design
    ↓
Implementation
    ↓
Testing
    ↓
Review
    ↓
Deployment
```

The agent MUST NOT immediately generate the entire application from a single prompt.

---

# 62. Agentic AI Development Instructions

The implementation agent should treat this document as the primary source of truth.

The agent MUST:

1. Read this entire specification before coding.
2. Identify ambiguities.
3. Create an implementation plan.
4. Break implementation into small tasks.
5. Implement one task at a time.
6. Run tests after meaningful changes.
7. Update documentation when behavior changes.
8. Never silently change requirements.
9. Ask for clarification when a requirement materially affects architecture or correctness.
10. Keep implementation consistent with this specification.

---

# 63. Agent Task Decomposition

The agent SHOULD divide implementation into phases.

## Phase 1 — Project Setup

Tasks:

```text
Initialize repository
Configure frontend
Configure backend
Configure database
Configure environment variables
Configure linting
Configure formatting
Configure testing
```

---

## Phase 2 — Database

Implement:

```text
users
categories
transactions
budgets
```

Then create migrations.

Tests MUST verify:

- constraints,
- relationships,
- uniqueness rules.

---

# 64. Phase 3 — Authentication

Implement:

```text
register
login
logout
authentication middleware
authorization
```

Test:

```text
valid login
invalid password
unknown user
duplicate email
protected endpoint
unauthorized resource access
```

---

# 65. Phase 4 — Transactions

Implement:

```text
create
read
update
delete
filter
search
sort
pagination
```

All transaction operations MUST respect user ownership.

---

# 66. Phase 5 — Budgets

Implement:

```text
create budget
update budget
delete budget
budget utilization
budget status
```

Implement the threshold logic defined in this specification.

---

# 67. Phase 6 — Dashboard

Implement:

```text
summary
category breakdown
monthly trend
budget status
```

All calculations should be tested independently.

---

# 68. Phase 7 — Frontend

Implement:

```text
login
register
dashboard
transactions
budgets
```

Prioritize:

1. correctness,
2. usability,
3. responsive design,
4. visual polish.

---

# 69. Phase 8 — Testing

Run:

```text
unit tests
integration tests
API tests
end-to-end tests
```

The agent MUST fix failing tests before deployment.

---

# 70. Phase 9 — Deployment

Deploy:

```text
frontend
backend
database
```

Configure:

```text
environment variables
CORS
production database
HTTPS
logging
```

---

# 71. Phase 10 — Documentation

README MUST contain:

```text
Project Overview
Features
Architecture
Technology Stack
Local Setup
Environment Variables
Database Setup
API Documentation
Testing
Deployment
Known Limitations
Future Improvements
```

---

# 72. Definition of Done

A feature is considered complete only when:

```text
Requirement implemented
        ↓
Code implemented
        ↓
Tests written
        ↓
Tests passing
        ↓
Error cases handled
        ↓
Documentation updated
```

---

# 73. MVP Definition of Done

The MVP is complete when:

- [ ] User registration works.
- [ ] Login works.
- [ ] Logout works.
- [ ] Authentication is secure.
- [ ] Users can create income.
- [ ] Users can create expenses.
- [ ] Users can edit transactions.
- [ ] Users can delete transactions.
- [ ] Categories work.
- [ ] Transaction filtering works.
- [ ] Transaction search works.
- [ ] Budgets can be created.
- [ ] Budget utilization works.
- [ ] Budget warnings work.
- [ ] Dashboard works.
- [ ] Charts work.
- [ ] Data isolation works.
- [ ] Unit tests exist.
- [ ] Integration tests exist.
- [ ] Application is deployed.
- [ ] README exists.
- [ ] No secrets are committed.

---

# 74. Optional Advanced Features

Only implement these AFTER the MVP is stable.

Potential additions:

### Recurring Transactions

Example:

```text
Rent
₹20,000
Every month
```

### CSV Import

Allow users to upload transaction data.

### CSV Export

Allow users to export their financial records.

### Dark Mode

Optional UI enhancement.

### Custom Categories

Allow users to define their own categories.

### Financial Insights

Generate insights such as:

```text
Your food spending increased 18% compared with last month.
```

These insights can later become an AI feature.

---

# 75. Optional AI Extension

AI is NOT required for Version 1.

If the core system is stable, an AI-powered insight module MAY be added.

Example:

```text
User financial data
        ↓
Aggregation
        ↓
Insight Generation
        ↓
LLM
        ↓
Natural Language Explanation
```

Example:

> "Your transportation expenses increased by 22% this month, mainly because of higher spending in the first two weeks."

IMPORTANT:

The LLM MUST NOT directly modify financial records.

The LLM should only interpret already-calculated data.

---

# 76. AI Safety Requirement

The application MUST NOT present generated insights as professional financial advice.

Avoid statements such as:

> "You should invest ₹20,000."

Prefer:

> "Your spending in the Entertainment category increased by 25% compared with last month."

---

# 77. Observability

The production application SHOULD provide:

```text
application logs
error logs
request logs
health check
```

Health endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

# 78. Health Checks

The backend health check SHOULD verify:

```text
application running
database connectivity
```

The health endpoint should not expose sensitive information.

---

# 79. Environment Configuration

The project MUST include:

```text
.env.example
```

Example:

```text
DATABASE_URL=
SECRET_KEY=
JWT_SECRET=
CORS_ORIGINS=
```

Actual `.env` files MUST NOT be committed.

---

# 80. Git Requirements

Use meaningful commits.

Examples:

```text
feat: add transaction creation API
feat: implement budget calculation
test: add budget utilization tests
fix: prevent unauthorized transaction access
docs: update API documentation
```

Avoid commits such as:

```text
stuff
changes
final
final2
working
```

---

# 81. Agent Coding Rules

The agent MUST follow these rules:

### Rule 1

Do not modify unrelated files.

### Rule 2

Do not introduce dependencies without justification.

### Rule 3

Do not duplicate business logic.

### Rule 4

Do not hard-code financial calculations in the frontend.

### Rule 5

Do not store passwords in plaintext.

### Rule 6

Do not expose secrets.

### Rule 7

Do not bypass tests simply to make the build pass.

### Rule 8

Do not silently remove failing functionality.

### Rule 9

Do not change the API contract without updating the specification.

### Rule 10

Prefer simple maintainable implementations over unnecessary abstraction.

---

# 82. Decision-Making Rule for the Agent

When multiple implementation choices are possible, prioritize:

```text
Correctness
    >
Security
    >
Maintainability
    >
Testability
    >
Performance
    >
Convenience
```

The agent should choose the simplest solution satisfying the requirements.

---

# 83. Ambiguity Handling

If the specification does not explicitly define a behavior:

### Level 1

Choose the simplest reasonable implementation.

### Level 2

Check consistency with existing requirements.

### Level 3

Document the assumption.

### Level 4

Ask the human if the decision materially affects:

- architecture,
- security,
- database schema,
- API contracts,
- user experience.

The agent MUST NOT repeatedly ask for clarification about trivial implementation choices.

---

# 84. Change Management

If a requirement changes:

```text
New Requirement
       ↓
Update SPEC.md
       ↓
Identify affected components
       ↓
Update tests
       ↓
Implement change
       ↓
Run regression tests
       ↓
Update documentation
```

The specification must remain synchronized with the implementation.

---

# 85. Viva Preparation Requirements

Because this project will be evaluated through a viva, the development process SHOULD maintain a `VIVA.md` file.

It should contain:

## Problem

What problem does the application solve?

## Architecture

Why was this architecture selected?

## Database

Why PostgreSQL?

Why these tables?

Why these relationships?

## Backend

Why FastAPI?

Why service/repository separation?

## Frontend

Why React/Next.js?

## Authentication

How does authentication work?

How are passwords stored?

## Security

How is unauthorized access prevented?

## Testing

How did you verify correctness?

## Deployment

How does the deployed system work?

## Trade-offs

What alternatives were considered?

## Limitations

What does the system NOT solve?

## Future Improvements

What would you build next?

---

# 86. ELI5 Explanation Requirement

For every major component, the project documentation SHOULD contain both:

```text
ELI5 explanation
Technical explanation
```

Example:

## PostgreSQL

### ELI5

> PostgreSQL is like a very organized digital notebook that stores all of our users, transactions, categories, and budgets and lets us find information reliably.

### Technical

> PostgreSQL is a relational database used to persist normalized entities such as users, transactions, categories, and budgets while enforcing constraints and relationships.

---

# 87. Viva Question Bank

The agent SHOULD prepare answers for questions such as:

### General

1. What problem does your application solve?
2. Why did you choose this project?
3. What are the main features?
4. What would happen if 100,000 users used it?

### SDD

5. What is Spec-Driven Development?
6. How did SDD influence your development process?
7. What was specified before implementation?
8. How did you handle requirement changes?

### Backend

9. Why FastAPI?
10. Why REST?
11. Why separate service and repository layers?
12. How does authentication work?

### Database

13. Why PostgreSQL?
14. Why not MongoDB?
15. What relationships exist between tables?
16. Why use UUIDs?
17. What indexes did you create?

### Security

18. How are passwords stored?
19. How do you prevent SQL injection?
20. How do you prevent users from accessing another user's transactions?

### Financial Logic

21. How do you calculate balance?
22. How do you calculate savings rate?
23. How do you calculate budget utilization?
24. What happens when income is zero?
25. How do you handle decimal precision?

### Testing

26. What did you test?
27. What edge cases did you consider?
28. How do you know the financial calculations are correct?

### Deployment

29. How is the frontend deployed?
30. How is the backend deployed?
31. Where is the database hosted?
32. How are secrets managed?

### Design

33. What is the biggest limitation of your application?
34. What would you change if you rebuilt it?
35. What happens if the database goes down?
36. How would you scale the system?

---

# 88. Success Criteria

The project should NOT be considered successful merely because:

```text
The application runs.
```

It is successful when:

```text
Correct requirements
        +
Good specification
        +
Clean implementation
        +
Reliable tests
        +
Secure design
        +
Working deployment
        +
Clear documentation
        +
Strong viva understanding
```

---

# 89. Final Product Vision

The final application should feel like a small but professionally engineered product rather than a classroom CRUD demo.

A user should be able to:

```text
Register
   ↓
Login
   ↓
Add income
   ↓
Add expenses
   ↓
Create budgets
   ↓
View dashboard
   ↓
Analyze spending
   ↓
Receive budget warnings
   ↓
Understand financial trends
```

The system should be:

```text
Simple
Reliable
Secure
Responsive
Tested
Deployable
Maintainable
```

---

# 90. Final Instruction to the Agent

**Do not start by generating the entire codebase.**

First:

1. Read `SPEC.md`.
2. Summarize your understanding.
3. Identify explicit requirements.
4. Identify assumptions.
5. Propose the implementation plan.
6. Propose the architecture.
7. Propose the database schema.
8. Wait for approval if a major architectural ambiguity exists.
9. Implement incrementally.
10. Test every major component.
11. Keep the specification and implementation synchronized.
12. Never claim a feature works without testing it.
13. At the end, provide:
    - implementation summary,
    - architecture summary,
    - test results,
    - deployment instructions,
    - known limitations,
    - viva preparation notes.

**The objective is not merely to generate code. The objective is to produce a system that the developer can understand, explain, test, deploy, and defend during a technical viva.**

---

# END OF SPECIFICATION