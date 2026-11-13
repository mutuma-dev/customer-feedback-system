"""The exact SMS texts we send. Kept in one place so wording is easy to change."""

# Sent to a painter to invite them to rate us (wording from the brief's mock-up).
INVITE_TEXT = (
    "CompanyX: Thanks for buying our paint! Rate us 1-5 for product, care and "
    "happiness. Reply e.g. 4 5 4"
)
# Sent when a painter's reply is not three numbers.
HELP_TEXT = "CompanyX: Sorry, we did not understand. Reply with three numbers 1-5, e.g. 4 5 4"
# Sent after a valid reply was saved.
THANKS_TEXT = "CompanyX: Thank you for your feedback!"
