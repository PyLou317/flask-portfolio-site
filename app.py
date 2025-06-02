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

projects_list = {
    1: {
        'id': 1,
        'name': 'Evergreen',
        'description': 'A personal finance tracker with smart categorization and budget setting, to help you manage your day-to-day spending.',
        'url': '',
        'img_path1': 'static/images/projects/evergreen_finance1.png',
        'img_path2': ''
        },
    
    2: {
        'id': 2,
        'name': 'Table Perks',
        'description': 'Mobile first restaurant loyalty app. Designed to incentavize guest to bring referrals by offering special deals and reward points for each visit.',
        'url': 'https://bring-a-friend-production.up.railway.app/',
        'img_path1': 'static/images/projects/table_perks1.png',
        'img_path2': ''
        },
    
    3: {
        'id': 3,
        'name': 'Portfolio Site',
        'description': 'A simple Flask portfolio site with Gmail contact form integration.',
        'url': '',
        'img_path1': 'static/images/projects/portfolio_code.png',
        'img_path2': ''
        }
}

projects_data = []
for p_id in projects_list:
    project_data = projects_list[p_id]
    projects_data.append( (project_data['id'], project_data['name'], project_data['description'], project_data['url'], project_data['img_path1'], project_data['img_path2']) )
    

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html', projects=projects_data)


@app.route("/project/<num>")
def project_detail(num):
    print(projects_list[int(num)])
    try:
        proj_dict = projects_list[int(num)]
    except:
        return f"<h1>Invalid value for Project: {num}</h1>"
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