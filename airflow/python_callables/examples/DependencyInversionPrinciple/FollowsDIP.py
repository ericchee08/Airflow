from typing import Protocol

# Define an abstract interface (Abstraction)
class INotificationSender(Protocol):
    def send(self, message: str):
        pass

# Low-level modules (Implementations of the abstraction)
class EmailSender(INotificationSender):
    def send(self, message: str):
        print(f"Sending Email: {message}")

class SmsSender(INotificationSender):
    def send(self, message: str):
        print(f"Sending SMS: {message}")

# High-level module (Now depends on abstraction, not concrete classes)
class NotificationService:
    def __init__(self, sender: INotificationSender):
        self.sender = sender  # Depends on abstraction

    def send_notification(self, message):
        self.sender.send(message)

# Usage
email_sender = EmailSender()
sms_sender = SmsSender()

notifier_email = NotificationService(email_sender)
notifier_sms = NotificationService(sms_sender)

notifier_email.send_notification("Hello via Email!")  # Works
notifier_sms.send_notification("Hello via SMS!")      # Works

# ----------------------------------------------------------------------

# New implementation without modifying NotificationService
class WhatsAppSender(INotificationSender):
    def send(self, message: str):
        print(f"Sending WhatsApp Message: {message}")

# Usage
whatsapp_sender = WhatsAppSender()
notifier_whatsapp = NotificationService(whatsapp_sender)

notifier_whatsapp.send_notification("Hello via WhatsApp!")  # Works