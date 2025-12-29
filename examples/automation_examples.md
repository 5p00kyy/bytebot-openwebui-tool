# ByteBot Automation Examples

This document provides practical examples of common automation tasks you can execute with the ByteBot OpenWebUI tool.

## Table of Contents

1. [Invoice Processing](#invoice-processing)
2. [Document Analysis](#document-analysis)
3. [Research Automation](#research-automation)
4. [Data Entry & Migration](#data-entry--migration)
5. [Report Generation](#report-generation)
6. [Web Scraping](#web-scraping)
7. [Email Automation](#email-automation)
8. [Multi-System Workflows](#multi-system-workflows)

---

## Invoice Processing

### Download Invoices from Vendor Portal

```python
execute_task(
    "Log into vendor.acme.com using credentials from 1Password, "
    "navigate to the Invoices section, "
    "filter by date range December 1-31, 2024, "
    "download all PDF invoices, "
    "save them to ~/Downloads/invoices/acme/december_2024/",
    priority="HIGH"
)
```

**Expected Duration:** 2-5 minutes  
**Use Case:** Monthly invoice collection from vendor portals

---

### Extract Invoice Data

```python
# First, attach invoice PDFs to your OpenWebUI message
execute_task_with_files(
    "Read all uploaded invoices and create a CSV file with: "
    "Invoice Number, Date, Vendor Name, Amount, Due Date. "
    "Save the CSV to ~/Downloads/invoice_summary.csv"
)
```

**Expected Duration:** 1-3 minutes per invoice  
**Use Case:** Invoice data entry automation

---

### Invoice Reconciliation

```python
execute_task(
    "Open the accounting system at accounting.company.com, "
    "download the December invoice register, "
    "compare it with files in ~/Downloads/invoices/acme/december_2024/, "
    "identify any missing or duplicate invoices, "
    "generate a reconciliation report in ~/Downloads/reconciliation_report.txt",
    priority="MEDIUM"
)
```

**Expected Duration:** 5-10 minutes  
**Use Case:** Monthly accounting reconciliation

---

## Document Analysis

### Contract Comparison

```python
# Attach 3-5 contract PDFs to your message
execute_task_with_files(
    "Compare these contracts and create a markdown table with columns: "
    "Contract Name, Payment Terms, Delivery Date, Penalty Clauses, "
    "Renewal Terms, Termination Notice Period. "
    "Highlight any unusual or concerning clauses."
)
```

**Expected Duration:** 2-4 minutes per contract  
**Use Case:** Legal document review

---

### Extract Key Dates

```python
# Attach policy documents or contracts
execute_task_with_files(
    "Read all uploaded documents and extract all dates mentioned. "
    "Create a chronological list with: Date, Document Name, Context. "
    "Flag any dates within the next 30 days as 'UPCOMING'."
)
```

**Expected Duration:** 1-2 minutes per document  
**Use Case:** Compliance deadline tracking

---

### Summarize Meeting Notes

```python
# Attach meeting transcripts or notes
execute_task_with_files(
    "Read these meeting notes and create a summary with: "
    "1. Key decisions made, "
    "2. Action items with assigned owners, "
    "3. Important dates or deadlines, "
    "4. Unresolved questions. "
    "Format as markdown with sections."
)
```

**Expected Duration:** 1-2 minutes  
**Use Case:** Meeting follow-up automation

---

## Research Automation

### Academic Paper Search

```python
execute_task(
    "Search arXiv.org for papers on 'quantum error correction' "
    "published in 2024, "
    "sort by citation count (most cited first), "
    "download the top 10 PDFs to ~/Downloads/papers/quantum_error_correction/, "
    "create a summary file listing: Title, Authors, Abstract, arXiv ID",
    priority="MEDIUM"
)
```

**Expected Duration:** 5-10 minutes  
**Use Case:** Literature review automation

---

### Competitive Intelligence

```python
execute_task(
    "Visit competitor websites: competitor1.com, competitor2.com, competitor3.com. "
    "For each, capture: Latest product announcements, pricing information, "
    "job postings, press releases from past month. "
    "Save findings to ~/Downloads/competitive_intel_report.md",
    priority="LOW"
)
```

**Expected Duration:** 10-15 minutes  
**Use Case:** Market research

---

### Technology Stack Research

```python
execute_task(
    "Research the technology stack for: React, Vue, Angular, Svelte. "
    "For each framework, find: Current stable version, release date, "
    "major features, TypeScript support, ecosystem size (npm packages), "
    "recent GitHub activity. "
    "Create a comparison table in ~/Downloads/framework_comparison.md"
)
```

**Expected Duration:** 8-12 minutes  
**Use Case:** Technology evaluation

---

## Data Entry & Migration

### CRM Data Entry

```python
# Attach a CSV with lead data
execute_task_with_files(
    "Log into CRM at crm.company.com, "
    "read the uploaded CSV file with columns: Name, Email, Company, Phone, Source. "
    "Create a new lead for each row. "
    "Tag all leads with 'Import_2024_12'. "
    "Save a log of successful and failed entries."
)
```

**Expected Duration:** 1-2 minutes per 10 leads  
**Use Case:** Bulk CRM import

---

### Database Migration

```python
execute_task(
    "Connect to legacy database at legacy-db.company.local, "
    "export all customer records from 'customers' table, "
    "transform data to match new schema (map old_field1 to new_field_a), "
    "save as CSV in ~/Downloads/customer_migration.csv. "
    "Do NOT modify the database, only read.",
    priority="URGENT"
)
```

**Expected Duration:** Varies by database size  
**Use Case:** System migration preparation

---

## Report Generation

### Sales Performance Report

```python
execute_task(
    "Log into sales dashboard at sales.company.com, "
    "export data for Q4 2024, "
    "calculate: Total revenue, Top 10 products, Sales by region, "
    "Month-over-month growth. "
    "Generate a PDF report with charts and save to ~/Downloads/sales_report_q4_2024.pdf",
    priority="HIGH"
)
```

**Expected Duration:** 5-8 minutes  
**Use Case:** Quarterly reporting

---

### Compliance Audit Report

```python
execute_task(
    "Review all files in ~/Documents/policies/, "
    "check for: Last updated date (flag if > 1 year old), "
    "Required signatures present, Proper version numbers. "
    "Generate compliance audit report listing all issues found. "
    "Save to ~/Downloads/compliance_audit.md"
)
```

**Expected Duration:** 3-5 minutes  
**Use Case:** Internal audits

---

## Web Scraping

### Job Posting Aggregation

```python
execute_task(
    "Search job boards: LinkedIn, Indeed, Glassdoor "
    "for 'Senior Python Developer' positions in 'San Francisco'. "
    "Collect: Job title, Company, Salary range (if listed), "
    "Required experience, Remote status. "
    "Save to ~/Downloads/job_postings.csv with 50 most recent postings",
    priority="LOW"
)
```

**Expected Duration:** 10-15 minutes  
**Use Case:** Job market research

---

### Price Monitoring

```python
execute_task(
    "Check prices for 'iPhone 15 Pro' on: Amazon, Best Buy, Apple Store, Walmart. "
    "Record: Current price, In stock status, Shipping time, Seller rating. "
    "Compare with previous prices from ~/Downloads/price_history.csv "
    "(if exists), flag any price drops > 10%. "
    "Update price_history.csv with new data."
)
```

**Expected Duration:** 3-5 minutes  
**Use Case:** Price tracking automation

---

## Email Automation

### Email Triage

```python
execute_task(
    "Log into webmail at mail.company.com, "
    "review all unread emails in Inbox, "
    "create folders: Urgent, Finance, HR, Marketing, Other. "
    "Move emails to appropriate folders based on subject and sender. "
    "Flag any emails from VIP list (CEO, CFO, customers) as high priority",
    priority="MEDIUM"
)
```

**Expected Duration:** 5-10 minutes  
**Use Case:** Email organization

---

### Newsletter Compilation

```python
execute_task(
    "Search news sources: TechCrunch, Hacker News, Ars Technica "
    "for articles about 'artificial intelligence' from past 7 days. "
    "Select top 5 most popular articles, "
    "create a newsletter digest with: Title, Summary (2 sentences), Link. "
    "Format as HTML and save to ~/Downloads/weekly_ai_digest.html"
)
```

**Expected Duration:** 8-12 minutes  
**Use Case:** Content curation

---

## Multi-System Workflows

### Customer Onboarding

```python
execute_task(
    "1. Read new customer data from ~/Downloads/new_customer.json, "
    "2. Log into CRM at crm.company.com and create customer account, "
    "3. Log into billing system at billing.company.com and set up billing profile, "
    "4. Log into ticketing system at support.company.com and create welcome ticket, "
    "5. Send confirmation email template from ~/Templates/welcome_email.html, "
    "6. Update customer status to 'Active' in all systems. "
    "Log all actions to ~/Downloads/onboarding_log.txt",
    priority="URGENT"
)
```

**Expected Duration:** 8-15 minutes  
**Use Case:** Multi-system customer setup

---

### End-of-Month Closing

```python
execute_task(
    "1. Log into accounting system and download month-end reports, "
    "2. Log into payroll system and verify all timesheets submitted, "
    "3. Log into expense system and check for unprocessed expenses, "
    "4. Generate summary report with: Total revenue, Total expenses, "
    "   Outstanding invoices, Pending approvals. "
    "5. Save all reports to ~/Downloads/eom_closing/2024_12/ "
    "6. Create checklist of incomplete items in eom_checklist.md",
    priority="HIGH"
)
```

**Expected Duration:** 15-25 minutes  
**Use Case:** Financial closing procedures

---

## Advanced Examples

### Conditional Workflow

```python
execute_task(
    "Check inventory levels at inventory.company.com. "
    "If any item quantity < 10: "
    "  - Add to reorder list "
    "  - Log into supplier portal and check availability "
    "  - Create purchase order if supplier has stock "
    "If critical items (flagged in system) < 5: "
    "  - Send urgent notification email to procurement@company.com "
    "Generate inventory report with reorder recommendations",
    priority="MEDIUM"
)
```

**Expected Duration:** 10-15 minutes  
**Use Case:** Inventory management automation

---

### Data Validation Pipeline

```python
# Attach data file
execute_task_with_files(
    "Read uploaded CSV file and validate: "
    "1. Email addresses are properly formatted, "
    "2. Phone numbers match pattern (XXX) XXX-XXXX, "
    "3. Zip codes are 5 digits, "
    "4. No duplicate entries based on email field, "
    "5. All required fields (name, email, company) are present. "
    "Create two files: "
    "- valid_records.csv (clean data), "
    "- validation_errors.txt (list of issues found)"
)
```

**Expected Duration:** 2-4 minutes  
**Use Case:** Data quality assurance

---

## Tips for Effective Automation

### Be Specific
```python
# Good
execute_task("Log into vendor.acme.com, click 'Invoices', filter December 2024, download all PDFs")

# Bad
execute_task("Get invoices")
```

### Include Credentials Source
```python
# Good
execute_task("Log into CRM using 1Password credentials")

# Bad
execute_task("Log into CRM with username admin and password ****")
```

### Specify File Paths
```python
# Good
execute_task("Save report to ~/Downloads/reports/sales_2024_q4.pdf")

# Bad
execute_task("Save report")
```

### Break Down Complex Tasks
```python
# For very complex workflows, break into steps:

# Step 1
execute_task("Download data from system A to ~/Downloads/data_a.csv")

# Step 2 (after step 1 completes)
execute_task("Download data from system B to ~/Downloads/data_b.csv")

# Step 3 (after both complete)
execute_task("Merge ~/Downloads/data_a.csv and data_b.csv, remove duplicates, save to final_report.csv")
```

---

## Monitoring Long-Running Tasks

For tasks that may take a while:

```python
# Submit without waiting
task_result = execute_task(
    "Process large dataset...",
    wait_for_completion=False
)
# Returns: Task ID: task-abc123

# Check status later
get_task_status("task-abc123")

# Or list all running tasks
list_tasks(status_filter="IN_PROGRESS")
```

---

## Error Recovery

If a task fails, review the error and try:

1. **Simplify the task** - Break into smaller steps
2. **Check credentials** - Verify in password manager
3. **Review logs** - Check ByteBot UI for details
4. **Add explicit waits** - "Wait 5 seconds for page to load"
5. **Provide more context** - Include exact field names, button text

---

## Best Practices Summary

1. **Test with simple tasks first** before complex workflows
2. **Use descriptive task descriptions** for better results
3. **Specify exact paths and dates** to avoid ambiguity
4. **Monitor task progress** with status checks
5. **Review ByteBot UI** when tasks need assistance
6. **Keep file uploads under 100MB** for better performance
7. **Use appropriate priority levels** to manage workload
8. **Document successful patterns** for reuse

---

For more examples and community-contributed automation scripts, visit the ByteBot Discord community or check the official documentation.
