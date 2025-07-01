from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf.csrf import CSRFProtect

from decouple import config
import smtplib
from email.mime.text import MIMEText
import json

app = Flask(__name__)
app.secret_key = config('FLASK_SECRET_KEY')
csrf = CSRFProtect(app)

# --- GMAIL SMTP Configuration ---
GMAIL_SENDER_EMAIL = config('GMAIL_SENDER_EMAIL', 'your_gmail_address@gmail.com')
GMAIL_APP_PASSWORD = config('GMAIL_APP_PASSWORD', 'your_gmail_app_password')
RECEIVER_EMAIL = config('RECEIVER_EMAIL', 'the_email_you_want_messages_sent_to@example.com')


# ----- Load Project Data ----- #
with open('data.json', 'r') as file:
    data = json.load(file)
projects = data.get("projects", [])
for project in projects:
    print("Project:", project)
    print("")
    

# ----- Views ----- #
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html', projects=projects)


@app.route("/project/<num>")
def project_detail(num):
    try:
        proj_id = int(num)
    except:
        return f"<h1>Invalid value for Project: {num}</h1>"
    
    proj_dict = None
    for project in projects:
        if project.get('id') == proj_id:
            proj_dict = project
    return render_template('project_detail.html', proj=proj_dict, project_name=proj_dict['name'])
    

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_content = request.form.get('message')

        if not name or not email or not subject or not message_content:
            flash('All fields are required. Please fill them out.', 'danger')
            return redirect(url_for('index') + '#contact-me')

        # Check if Gmail API Key is set
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
                smtp.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                smtp.send_message(msg)

            flash('Your message has been sent successfully! Thank you.', 'success')
            
        except Exception as e:
            print(f"An unexpected error occurred during email sending: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')

        return redirect(url_for('index') + '#contact-me')

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=config("PORT", default=5000))
    
    
# {
# "id": 2,
# "name": "Table Perks",
# "description": "Mobile first restaurant loyalty app. Designed to incentavize guest to bring referrals by offering special deals and reward points for each visit.",
# "url": "https://bring-a-friend-production.up.railway.app/",
# "img_path1": "static/images/projects/table_perks/mobile3.png",
# "img_path2": "",
# "img_path3": "",
# "img_path4": ""
# },