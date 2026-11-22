"""Labels and business rules shared by the database, the API, and the pages."""

ENQUIRY_STATUSES = [
    ("new", "New"),
    ("contacted", "Contacted"),
    ("follow_up", "Follow-up Required"),
    ("negotiation", "Negotiation"),
    ("converted", "Converted"),
    ("rejected", "Rejected"),
]

# A new enquiry has not been worked yet, so it is not in the conversion ratio.
# Conversion rate = converted / eligible × 100.
ELIGIBLE_ENQUIRY_STATUSES = ("contacted", "follow_up", "negotiation", "converted", "rejected")
OPEN_ENQUIRY_STATUSES = ("new", "contacted", "follow_up", "negotiation")
CONVERTED_STATUS = "converted"

BOOKING_STATUSES = [
    ("confirmed", "Confirmed"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("on_hold", "On Hold"),
]
ACTIVE_BOOKING_STATUSES = ("confirmed", "in_progress", "completed")
UPCOMING_BOOKING_STATUSES = ("confirmed", "in_progress", "on_hold")

PROJECT_STATUSES = [
    ("not_started", "Not Started"),
    ("in_progress", "In Progress"),
    ("editing", "Editing"),
    ("review", "Review"),
    ("completed", "Completed"),
    ("delivered", "Delivered"),
]
DONE_PROJECT_STATUSES = ("completed", "delivered")
EMPLOYEE_PROJECT_FIELDS = {"status", "notes"}

PAYMENT_METHODS = [
    ("upi", "UPI"),
    ("cash", "Cash"),
    ("bank_transfer", "Bank Transfer"),
    ("card", "Card"),
    ("other", "Other"),
]

PAYMENT_STATUSES = [
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("partially_paid", "Partially Paid"),
    ("refunded", "Refunded"),
]
# Cash that has actually arrived. Pending is excluded. Refunds are subtracted.
COLLECTED_PAYMENT_STATUSES = ("paid", "partially_paid")

TEAM_ROLES = [
    "Lead Photographer",
    "Photographer",
    "Cinematographer",
    "Editor",
    "Assistant",
    "Coordinator",
]

# North-Indian wedding calendar used as a labeled business rule for seasonal analysis.
# It is a teaching assumption for this demo, not a claim about a real studio.
WEDDING_SEASONS = [
    ("Peak wedding season", (11, 12, 1, 2)),
    ("Moderate", (3, 4, 10)),
    ("Lean months", (5, 6, 7, 8, 9)),
]

CONVERSION_DEFINITION = (
    "Conversion rate = (Converted enquiries / Eligible enquiries) × 100. "
    "Eligible statuses are Contacted, Follow-up Required, Negotiation, Converted, and Rejected. "
    "Status New is excluded because nobody has worked that enquiry yet."
)

REVENUE_DEFINITION = (
    "Revenue is money actually recorded in the payments table. "
    "Paid and Partially Paid amounts are added. Refunded amounts are subtracted. "
    "Pending amounts are ignored. The full booking contract is not treated as revenue "
    "when only an advance has been collected."
)

STATUS_LABELS = dict(
    ENQUIRY_STATUSES
    + BOOKING_STATUSES
    + PROJECT_STATUSES
    + PAYMENT_METHODS
    + PAYMENT_STATUSES
    + [("active", "Active"), ("inactive", "Inactive"), ("admin", "Admin"), ("employee", "Employee")]
)

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
