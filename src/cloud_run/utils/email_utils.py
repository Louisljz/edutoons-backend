import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email_to_user(video_url, projectId, recipient_email):
    sg_api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")

    subject = f"Your video for project {projectId} is ready!"
    html_content = f"""
    <p>Hi there,</p>
    <p>Your video is ready and can be accessed <a href="{video_url}">here</a>.</p>
    <p>Best regards,<br>EduToons</p>
    """

    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(sg_api_key)
        response = sg.send(message)

        print(f"Email sent to {recipient_email}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")
