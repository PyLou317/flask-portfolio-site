from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf.csrf import CSRFProtect

from decouple import config
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = config('FLASK_SECRET_KEY')
csrf = CSRFProtect(app)

# --- GMAIL SMTP Configuration ---
GMAIL_SENDER_EMAIL = config('GMAIL_SENDER_EMAIL', 'your_gmail_address@gmail.com')
GMAIL_APP_PASSWORD = config('GMAIL_APP_PASSWORD', 'your_gmail_app_password')
RECEIVER_EMAIL = config('RECEIVER_EMAIL', 'the_email_you_want_messages_sent_to@example.com')


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_content = request.form.get('message')

        # Basic validation
        if not name or not email or not subject or not message_content:
            flash('All fields are required. Please fill them out.', 'danger')
            return redirect(url_for('index') + '#contact-me')

        # Check if SendGrid API Key is set
        if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
            flash('Server error: Email sending credentials not configured.', 'danger')
            print("GMAIL_SENDER_EMAIL or GMAIL_APP_PASSWORD is not set in environment variables!")
            return redirect(url_for('index') + '#contact-me')

        try:
            msg = MIMEText(f"""
            Name: {name}
            Email: {email}
            Subject: {subject}

            Message:
            {message_content}
            """)
            
            msg['Subject'] = f'New Contact Form Submission: {subject} from {name}'
            msg['From'] = GMAIL_SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            msg['Reply-To'] = email

            # Connect to Gmail's SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                # Log in to Gmail account
                smtp.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                # Send the email
                smtp.send_message(msg)

            flash('Your message has been sent successfully! Thank you.', 'success')
            
        except Exception as e:
            print(f"An unexpected error occurred during email sending: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')

        return redirect(url_for('index') + '#contact-me')

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=8000)