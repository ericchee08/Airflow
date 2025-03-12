# Low-level modules (Concrete Implementations)
class EmailSender:
    def send(self, message):
        print(f"Sending Email: {message}")

class SmsSender:
    def send(self, message):
        print(f"Sending SMS: {message}")

# High-level module (Tightly coupled to specific implementations)
class NotificationService:
    def __init__(self, email_sender: EmailSender, sms_sender: SmsSender):
        self.email_sender = email_sender
        self.sms_sender = sms_sender

    def send_email_notification(self, message):
        self.email_sender.send(message)

    def send_sms_notification(self, message):
        self.sms_sender.send(message)

# Usage
email_sender = EmailSender()
sms_sender = SmsSender()
notifier = NotificationService(email_sender, sms_sender)

notifier.send_email_notification("Hello via Email!")
notifier.send_sms_notification("Hello via SMS!")      