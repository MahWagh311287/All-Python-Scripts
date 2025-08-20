import subprocess
import os
import pwd
import random
import string
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ----------- Helper function to run shell commands ------------
def run_command(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
    return result


# ----------- Random Password Generator ------------------------
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))


# ----------- Email Service (Modified for user email) ----------
class EmailService:
    def __init__(self):
        self.mail_fromaddr = "support@acuitilabs.com"
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587

    def sendmail(self, toaddr, subject, body):
        try:
            mail_msg = MIMEMultipart()
            mail_msg['From'] = self.mail_fromaddr
            mail_msg['To'] = toaddr
            mail_msg['Subject'] = subject
            mail_msg.attach(MIMEText(body, 'html'))

            mail_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            mail_server.starttls()

            password = os.getenv('EMAIL_PASSWORD', 'IThelp24x7@acuiti')  # App password recommended
            mail_server.login(self.mail_fromaddr, password)

            mail_server.sendmail(self.mail_fromaddr, [toaddr], mail_msg.as_string())
            print(f"Mail sent successfully to {toaddr}")

            mail_server.quit()
            return True

        except smtplib.SMTPException as e:
            print(f"Error while sending email: {e}")
            return False


# ----------- User Creation Function -------------------------
def create_user(username):
    try:
        # check if user exists
        try:
            pwd.getpwnam(username)
            print(f"User {username} already exists. Skipping creation...")
            return None
        except KeyError:
            pass  # user doesn't exist, continue

        # generate password
        password = generate_password()

        # create user
        run_command(f"useradd -m {username}")

        # set password
        run_command(f"echo '{username}:{password}' | chpasswd")

        # add user to group
        run_command(f"usermod -aG mzdev {username}")

        # create shared symlink
        shared_dir = "/opt/mz/shared_directory"
        user_shared = f"/home/{username}/shared"
        if os.path.exists(shared_dir):
            if not os.path.exists(user_shared):
                os.symlink(shared_dir, user_shared)

        print(f"User {username} created successfully.")
        return password

    except Exception as e:
        print(f"Unexpected error while creating user {username}: {e}")
        return None


# ----------- Main Execution --------------------------
def main():
    users = ["sowmya.a", "ketan.s"]

    email_service = EmailService()
    server_ip = socket.gethostbyname(socket.gethostname())

    for username in users:
        password = create_user(username)

        if password:
            user_email = f"{username}@acuitilabs.com"

            email_body = f"""
            <html>
            <body style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; color: #333; background-color:#f9f9f9; padding:20px;">

                <div style="max-width:600px; margin:auto; background:#ffffff; border:1px solid #ddd; border-radius:8px; padding:20px;">
                    
                    <h2 style="color:#004080; text-align:center;">Linux Account Created</h2>
                    
                    <p style="font-size:14px;">Dear <b style="color:#333;">{username}</b>,</p>

                    <p style="font-size:14px;">Your Linux account has been successfully created on the server.</p>

                    <table border="0" cellspacing="0" cellpadding="10" style="width:100%; border:1px solid #ccc; border-collapse:collapse; margin-top:15px;">
                        <tr style="background-color:#004080; color:#ffffff; text-align:left;">
                            <th style="width:30%;">Detail</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ccc;"><b>Server IP</b></td>
                            <td style="border:1px solid #ccc;">{server_ip}</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ccc;"><b>Username</b></td>
                            <td style="border:1px solid #ccc;">{username}</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ccc;"><b>Password</b></td>
                            <td style="border:1px solid #ccc; color:#d9534f; font-weight:bold;">{password}</td>
                        </tr>
                    </table>

                    <p style="margin-top:20px; font-size:20px; color:#d9534f;">
                        ⚠️ Please change your password immediately after first login for security reasons.
                    </p>

                    <br>
                    <p style="font-size:14px;">Regards,<br>
                    <b style="color:#004080;">IT Support Team</b><br>
                    Acuiti Labs</p>
                </div>
            </body>
            </html>
            """

            email_service.sendmail(user_email, "Your Linux Account Details", email_body)


if __name__ == "__main__":
    main()
