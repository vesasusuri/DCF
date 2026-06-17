"""Shared domain constants for projects and valuation workflow."""

PROJECT_STATUS_DRAFT = "draft"
PROJECT_STATUS_TEST = "test"
PROJECT_STATUS_READY = "ready"
PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_ARCHIVED = "archived"

PROJECT_STATUSES = frozenset(
    {
        PROJECT_STATUS_DRAFT,
        PROJECT_STATUS_TEST,
        PROJECT_STATUS_READY,
        PROJECT_STATUS_ACTIVE,
        PROJECT_STATUS_ARCHIVED,
    }
)

NON_ARCHIVED_STATUSES = frozenset(
    {
        PROJECT_STATUS_DRAFT,
        PROJECT_STATUS_TEST,
        PROJECT_STATUS_READY,
        PROJECT_STATUS_ACTIVE,
    }
)

# Projects in test status are awaiting data/quality review before promotion.
AWAITING_REVIEW_PROJECT_STATUSES = frozenset({PROJECT_STATUS_TEST})

# Valuation runs in these states still need portfolio manager attention.
AWAITING_REVIEW_RUN_STATUSES = frozenset({"pending", "review"})
