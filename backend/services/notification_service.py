"""Notification provider boundary."""

class NotificationService:
    def notify(self, user, channel, message, meta=None):
        """
        channel: sms | push | whatsapp | email

        A production provider must be configured before delivery is attempted.
        """
        raise RuntimeError("No notification provider is configured.")

    def broadcast_sos(self, user, contacts, payload):
        """Fan an SOS to every listed contact. Real system: parallel SMS + push."""
        return [
            self.notify(user, "sms", f"SOS from {user.name}", meta={"contact": c})
            for c in contacts
        ]
