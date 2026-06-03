from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DomainProfile:
    path_terms: List[str] = field(default_factory=list)
    name_terms: List[str] = field(default_factory=list)
    identifier_terms: List[str] = field(default_factory=list)
    import_terms: List[str] = field(default_factory=list)
    table_terms: List[str] = field(default_factory=list)
    flag_boosts: Dict[str, float] = field(default_factory=dict)


# Weights align with common static-analysis practice (path > deps > symbols > flags).
PATH_WEIGHT = 4.0
NAME_WEIGHT = 3.5
IMPORT_WEIGHT = 3.0
IDENTIFIER_WEIGHT = 2.5
TABLE_WEIGHT = 2.0
FLAG_WEIGHT = 3.0

# Calibrated so strong multi-signal files approach 1.0 without saturating weak files.
SCORE_SCALE = 12.0

MIN_REPORTED_SCORE = 0.30
MIN_PRIMARY_SCORE = 0.35
GRAPH_PROPAGATION_FACTOR = 0.18

DOMAIN_PROFILES: Dict[str, DomainProfile] = {
    "Finance": DomainProfile(
        path_terms=[
            "finance", "financial", "fintech", "banking", "bank", "payment",
            "payments", "billing", "invoice", "ledger", "accounting", "treasury",
            "reconciliation", "settlement", "merchant", "trading", "portfolio",
            "tax", "vat", "payroll_gl", "accounts_payable", "accounts_receivable",
        ],
        name_terms=[
            "payment", "invoice", "ledger", "transaction", "billing", "wallet",
            "stripe", "paypal", "swift_mt", "iban", "ach", "sepa", "dividend",
            "reconcile", "journal_entry", "general_ledger",
        ],
        identifier_terms=[
            "payment", "invoice", "ledger", "transaction", "billing", "wallet",
            "transfer", "debit", "credit", "balance", "interest", "loan",
            "mortgage", "dividend", "portfolio", "reconcile", "settlement",
            "currency", "fx", "forex", "iban", "swift", "ach", "sepa",
            "stripe", "paypal", "braintree", "plaid", "quickbooks", "xero",
            "sap_fi", "oracle_financial", "general_ledger", "chart_of_accounts",
        ],
        import_terms=[
            "stripe", "paypal", "braintree", "plaid", "quickbooks", "xero",
            "money", "decimal", "iban", "swift", "ach", "sepa", "forex",
            "accounting", "ledger", "payment", "billing", "fintech",
        ],
        table_terms=[
            "transactions", "invoices", "payments", "ledger", "accounts",
            "journal", "budget", "balances", "wallets", "orders_payment",
        ],
        flag_boosts={},
    ),
    "Healthcare": DomainProfile(
        path_terms=[
            "health", "healthcare", "clinical", "medical", "hospital", "patient",
            "pharmacy", "ehr", "emr", "fhir", "hl7", "dicom", "telehealth",
            "diagnostics", "radiology", "pathology", "nursing", "hipaa",
        ],
        name_terms=[
            "patient", "clinical", "diagnosis", "prescription", "fhir", "hl7",
            "dicom", "ehr", "emr", "hipaa", "icd", "cpt", "snomed", "loinc",
        ],
        identifier_terms=[
            "patient", "clinical", "diagnosis", "prescription", "encounter",
            "observation", "condition", "procedure", "medication", "allergy",
            "vital", "lab_result", "radiology", "pathology", "admission",
            "discharge", "provider", "practitioner", "fhir", "hl7", "dicom",
            "hipaa", "icd10", "cpt", "snomed", "loinc", "epic", "cerner",
            "telehealth", "pharmacy", "immunization",
        ],
        import_terms=[
            "fhir", "hl7", "dicom", "pydicom", "health", "clinical", "patient",
            "medical", "snomed", "loinc", "epic", "cerner", "hipaa",
        ],
        table_terms=[
            "patients", "encounters", "prescriptions", "diagnoses", "providers",
            "claims_medical", "lab_results", "vitals",
        ],
        flag_boosts={"contains_auth_usage": 0.04},
    ),
    "Government": DomainProfile(
        path_terms=[
            "government", "gov", "public_sector", "civic", "municipal",
            "citizen", "regulatory", "compliance", "permits", "licensing",
            "election", "voting", "census", "tax_authority", "customs",
        ],
        name_terms=[
            "citizen", "passport", "visa", "permit", "license", "census",
            "election", "ballot", "municipal", "regulatory", "foia",
            "government", "public_record", "tax_return", "customs",
        ],
        identifier_terms=[
            "citizen", "passport", "visa", "permit", "license", "census",
            "election", "ballot", "voting", "municipal", "regulatory",
            "compliance", "foia", "subpoena_gov", "public_sector",
            "tax_return", "customs", "immigration", "border", "docket_gov",
            "agency", "department", "ordinance", "statute",
        ],
        import_terms=[
            "government", "gov", "civic", "regulatory", "compliance",
            "citizen", "passport", "election", "census",
        ],
        table_terms=[
            "citizens", "permits", "licenses", "applications_gov", "cases_gov",
        ],
        flag_boosts={"contains_auth_usage": 0.04},
    ),
    "Education": DomainProfile(
        path_terms=[
            "education", "academic", "school", "university", "college", "campus",
            "student", "course", "curriculum", "lms", "learning", "classroom",
            "faculty", "enrollment", "grading",
        ],
        name_terms=[
            "student", "course", "curriculum", "syllabus", "assignment", "grade",
            "enrollment", "faculty", "tuition", "quiz", "homework", "lms",
            "moodle", "canvas", "blackboard",
        ],
        identifier_terms=[
            "student", "course", "curriculum", "syllabus", "assignment", "grade",
            "enrollment", "faculty", "professor", "instructor", "tuition",
            "quiz", "exam", "homework", "lesson", "module", "semester",
            "academic", "campus", "degree", "diploma", "transcript",
            "moodle", "canvas", "blackboard", "school", "university",
        ],
        import_terms=[
            "moodle", "canvas", "blackboard", "education", "academic",
            "student", "course", "lms", "learning",
        ],
        table_terms=[
            "students", "courses", "enrollments", "assignments", "grades",
            "faculty", "classes",
        ],
        flag_boosts={},
    ),
    "Retail": DomainProfile(
        path_terms=[
            "retail", "ecommerce", "e-commerce", "commerce", "shop", "store",
            "catalog", "inventory", "warehouse", "fulfillment", "pos",
            "merchandising", "loyalty", "checkout", "cart",
        ],
        name_terms=[
            "product", "sku", "catalog", "inventory", "cart", "checkout",
            "order", "shipment", "fulfillment", "warehouse", "pos", "retail",
            "coupon", "loyalty", "merchandise",
        ],
        identifier_terms=[
            "product", "sku", "catalog", "inventory", "cart", "checkout",
            "order", "shipment", "fulfillment", "warehouse", "pos",
            "coupon", "loyalty", "discount", "merchandise", "variant",
            "stock", "quantity", "barcode", "shopify", "magento", "woocommerce",
            "amazon_sp", "marketplace",
        ],
        import_terms=[
            "shopify", "magento", "woocommerce", "commerce", "retail",
            "inventory", "catalog", "cart", "checkout", "stripe_checkout",
        ],
        table_terms=[
            "products", "orders", "carts", "inventory", "skus", "customers_shop",
            "shipments", "warehouses",
        ],
        flag_boosts={"contains_network_access": 0.05},
    ),
    "Telecom": DomainProfile(
        path_terms=[
            "telecom", "telecommunications", "carrier", "mobile", "wireless",
            "network_ops", "bss", "oss", "provisioning", "cdr", "sms", "voip",
            "5g", "lte", "sim", "subscriber",
        ],
        name_terms=[
            "subscriber", "sim", "msisdn", "imsi", "cdr", "bss", "oss",
            "roaming", "tariff", "bandwidth", "voip", "sms", "mms", "carrier",
            "provisioning", "telecom",
        ],
        identifier_terms=[
            "subscriber", "sim", "msisdn", "imsi", "cdr", "bss", "oss",
            "roaming", "tariff", "bandwidth", "voip", "sms", "mms",
            "carrier", "provisioning", "telecom", "network_operator",
            "cell_tower", "base_station", "lte", "5g", "nr", "diameter",
            "sip", "rtp", "twilio", "telco",
        ],
        import_terms=[
            "twilio", "telco", "telecom", "sip", "voip", "sms", "carrier",
            "subscriber", "provisioning", "oss", "bss",
        ],
        table_terms=[
            "subscribers", "cdr", "sim_cards", "plans", "usage_records",
        ],
        flag_boosts={"contains_network_access": 0.08},
    ),
    "Legal": DomainProfile(
        path_terms=[
            "legal", "law", "litigation", "contract", "counsel", "attorney",
            "compliance_legal", "discovery", "patent", "trademark", "copyright",
            "nda", "clause",
        ],
        name_terms=[
            "contract", "clause", "litigation", "attorney", "counsel", "legal",
            "nda", "agreement", "docket", "discovery", "subpoena", "patent",
            "trademark", "copyright", "compliance", "gdpr", "privacy_policy",
        ],
        identifier_terms=[
            "contract", "clause", "litigation", "attorney", "counsel", "legal",
            "nda", "agreement", "docket", "discovery", "subpoena", "patent",
            "trademark", "copyright", "compliance", "gdpr", "ccpa",
            "privacy", "terms_of_service", "legal_hold", "e_discovery",
            "redline", "amendment", "jurisdiction", "arbitration",
        ],
        import_terms=[
            "legal", "contract", "compliance", "gdpr", "privacy", "docusign",
            "clio", "ironclad",
        ],
        table_terms=[
            "contracts", "cases", "clauses", "agreements", "matters",
        ],
        flag_boosts={},
    ),
    "HR": DomainProfile(
        path_terms=[
            "hr", "human_resources", "human-resources", "people_ops",
            "peopleops", "talent", "recruiting", "recruitment", "payroll",
            "benefits", "onboarding", "workforce", "hcm",
        ],
        name_terms=[
            "employee", "payroll", "benefits", "onboarding", "recruiter",
            "hiring", "resume", "leave", "pto", "compensation", "headcount",
            "performance_review", "hris", "workday", "bamboo",
        ],
        identifier_terms=[
            "employee", "employer", "payroll", "benefits", "onboarding",
            "recruiter", "hiring", "candidate", "resume", "cv", "leave",
            "pto", "vacation", "compensation", "salary", "bonus",
            "performance_review", "headcount", "org_chart", "department_hr",
            "workday", "bamboohr", "greenhouse", "lever", "adp", "gusto",
            "timesheet", "attendance", "termination", "offer_letter",
        ],
        import_terms=[
            "workday", "bamboohr", "greenhouse", "lever", "adp", "gusto",
            "hris", "payroll", "recruiting", "talent",
        ],
        table_terms=[
            "employees", "payroll", "benefits", "candidates", "jobs", "departments",
            "time_off", "performance_reviews",
        ],
        flag_boosts={},
    ),
    "Security": DomainProfile(
        path_terms=[
            "security", "infosec", "cyber", "crypto", "cryptography", "auth",
            "authentication", "authorization", "iam", "identity", "acl",
            "firewall", "siem", "vault", "secrets", "pentest", "vulnerability",
        ],
        name_terms=[
            "security", "crypto", "encrypt", "decrypt", "auth", "oauth",
            "jwt", "rbac", "acl", "certificate", "tls", "ssl", "hash",
            "firewall", "intrusion", "malware", "vulnerability", "siem",
            "credential", "secret", "mfa", "totp", "hmac", "cipher",
        ],
        identifier_terms=[
            "security", "crypto", "encrypt", "decrypt", "auth", "authenticate",
            "oauth", "oidc", "jwt", "rbac", "acl", "certificate", "tls", "ssl",
            "hash", "hmac", "cipher", "firewall", "intrusion", "malware",
            "vulnerability", "siem", "credential", "secret", "mfa", "totp",
            "bcrypt", "argon", "scrypt", "pbkdf", "aes", "rsa", "ecdsa",
            "passport_strategy", "bcrypt", "passlib", "cryptography",
            "keycloak", "okta", "auth0", "vault", "kms", "hsm",
        ],
        import_terms=[
            "cryptography", "crypto", "hashlib", "bcrypt", "passlib", "jwt",
            "oauth", "authlib", "ssl", "tls", "nacl", "pycryptodome",
            "keycloak", "okta", "auth0", "vault", "boto3_kms", "secrets",
            "security", "firewall", "siem",
        ],
        table_terms=[
            "users", "roles", "permissions", "audit_log", "sessions", "tokens",
        ],
        flag_boosts={
            "contains_crypto_usage": 0.35,
            "contains_auth_usage": 0.25,
            "contains_network_access": 0.06,
            "contains_backup_logic": 0.05,
        },
    ),
}
