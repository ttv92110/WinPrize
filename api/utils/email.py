import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart  
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

class EmailService:
    def __init__(self):
        # Email configuration - Update with your email settings
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.smtp_user = os.getenv("SMTP_USER", "your-email@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "your-app-password")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@winprize.com")
        self.from_name = os.getenv("FROM_NAME", "WinPrize Support")
        
          # Setup templates
        base_dir = Path(__file__).parent.parent.parent
        templates_dir = base_dir / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))
    
    async def send_verification_pin(self, to_email: str, user_name: str, pin: str): 
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your WinPrize Email"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            html_content = self.templates.TemplateResponse(
                "emails/email_verification_pin.html",
                {
                    "request": None,
                    "user_name": user_name,
                    "pin": pin
                }
            ).body.decode()
            
            # Create plain text version
            text_content = f"""
            Hello {user_name},
            
            Thank you for registering with WinPrize! Your verification PIN is:
            
            {pin}
            
            This PIN will expire in 20 minutes.
            
            If you didn't request this verification, please ignore this email.
            
            Thanks,
            WinPrize Team
            """
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=120
            )
            
            print(f"Verification PIN sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending verification PIN: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_link: str, user_name: str):
        """Send password reset email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your WinPrize Password"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            
            html_content = self.templates.TemplateResponse(
                "emails/email_password_reset.html",
                {
                    "request": None,
                    "user_name": user_name,
                    "reset_link": reset_link
                }
            ).body.decode()
            
            # Create plain text version
            text_content = f"""
            Hello {user_name},
            
            We received a request to reset your password for your WinPrize account.
            
            Click the link below to create a new password:
            {reset_link}
            
            This link will expire in 1 hour and can only be used once.
            
            If you didn't request this, please ignore this email.
            
            Thanks,
            WinPrize Team
            """
            
            # Attach parts
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=120
            )
            
            print(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    async def send_welcome_email(self, to_email: str, user_name: str):
        """Send welcome email to new users"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Welcome to WinPrize!"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            
            html_content = self.templates.TemplateResponse(
                "emails/email_welcome.html",
                {
                    "request": None,
                    "user_name": user_name
                }
            ).body.decode()
            
            text_content = f"""
            Hello {user_name},
            
            Welcome to WinPrize! Your account has been successfully created.
            
            Start participating in exciting lucky draws and win amazing prizes!
            
            Visit https://winprize.vercel.app to get started.
            
            Good luck!
            WinPrize Team
            """
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=120
            )
            
            
            print(f"Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            return False
     
    async def send_new_draw_notification(self, to_email: str, user_name: str, draw_title: str, draw_prize: int, draw_fee: int):
        """Send email notification for new draw using template"""
        try:
            # Render HTML template
            html_content = self.templates.TemplateResponse(
                "emails/email_new_draw.html",
                {
                    "request": None,  # Request not needed for email
                    "user_name": user_name,
                    "draw_title": draw_title,
                    "draw_prize": draw_prize,
                    "draw_fee": draw_fee
                }
            ).body.decode()
            
            # Plain text version
            text_content = f"""
            New Lucky Draw Added!
            
            Hello {user_name},
            
            A new lucky draw has been added to WinPrize!
            
            Draw: {draw_title}
            Entry Fee: Rs. {draw_fee}
            Prize Pool: Rs. {draw_prize}
            
            Don't miss this chance to win big!
            
            Visit WinPrize to join: https://winprize.onrender.com
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 New Lucky Draw Added - WinPrize"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=120
            )
            
            print(f"New draw notification email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending new draw notification: {str(e)}")
            return False
    
    async def send_draw_result_notification(self, to_email: str, user_name: str, draw_title: str, is_winner: bool, prize_amount: int = 0):
        """Send email notification for draw result using template"""
        try:
            # Choose template based on winner/loser
            if is_winner:
                template_name = "emails/email_winner.html"
                subject = "🏆 Congratulations! You Won WinPrize Draw!"
            else:
                template_name = "emails/email_loser.html"
                subject = "😢 Draw Result Announced - WinPrize"
            
            # Render HTML template
            html_content = self.templates.TemplateResponse(
                template_name,
                {
                    "request": None,
                    "user_name": user_name,
                    "draw_title": draw_title,
                    "prize_amount": prize_amount
                }
            ).body.decode()
            
            # Plain text version
            if is_winner:
                text_content = f"""
                Congratulations! You Won!
                
                Hello {user_name},
                
                You are the winner of {draw_title}!
                You have won: Rs. {prize_amount}
                
                The prize amount will be credited to your account soon.
                
                View winners: https://winprize.onrender.com/winner
                """
            else:
                text_content = f"""
                Draw Result Announced
                
                Hello {user_name},
                
                The winner for {draw_title} has been announced.
                Unfortunately, you didn't win this time.
                
                Don't worry! More draws are coming soon.
                
                View active draws: https://winprize.onrender.com/#draws
                """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                timeout=120
            )
            
            print(f"Draw result notification email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending draw result notification: {str(e)}")
            return False
    

# await aiosmtplib.send(
#     message,
#     hostname=self.smtp_host,
#     port=self.smtp_port,
#     username=self.smtp_user,
#     password=self.smtp_password,
#     start_tls=True
# )