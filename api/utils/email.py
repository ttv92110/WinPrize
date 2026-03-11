import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api.config import Config
import os

class EmailService:
    def __init__(self):
        # Email configuration - Update with your email settings
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "your-email@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "your-app-password")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@winprize.com")
        self.from_name = os.getenv("FROM_NAME", "WinPrize Support")
    
    async def send_verification_pin(self, to_email: str, user_name: str, pin: str):
        """Send 6-digit verification PIN"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your WinPrize Email"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Poppins', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header i {{
                        font-size: 60px;
                        margin-bottom: 15px;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .pin-box {{
                        background: linear-gradient(135deg, #667eea20, #764ba220);
                        border: 3px dashed #667eea;
                        border-radius: 20px;
                        padding: 30px;
                        margin: 30px 0;
                    }}
                    .pin {{
                        font-size: 48px;
                        font-weight: 800;
                        letter-spacing: 15px;
                        color: #667eea;
                        font-family: monospace;
                    }}
                    .info-box {{
                        background: #f8f9fa;
                        border-left: 4px solid #ffc107;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 30px 0;
                        text-align: left;
                    }}
                    .timer {{
                        font-size: 24px;
                        color: #dc3545;
                        font-weight: 600;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #dee2e6;
                    }}
                    
                   
                    @media screen and (max-width: 600px) {{
                        .container {{
                            max-width: 100% !important;
                            margin: 0 10px !important;
                        }}
                        
                        .header {{
                            padding: 30px 20px !important;
                        }}
                        
                        .header i {{
                            font-size: 40px !important;
                            margin-bottom: 10px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 22px !important;
                        }}
                        
                        .content {{
                            padding: 30px 20px !important;
                        }}
                        
                        .content p {{
                            font-size: 14px !important;
                            line-height: 1.5 !important;
                        }}
                        
                        .pin-box {{
                            padding: 20px !important;
                            margin: 20px 0 !important;
                        }}
                        
                        .pin {{
                            font-size: 32px !important;
                            letter-spacing: 8px !important;
                        }}
                        
                        .info-box {{
                            padding: 15px !important;
                            margin: 20px 0 !important;
                        }}
                        
                        .info-box p {{
                            font-size: 13px !important;
                            margin: 3px 0 !important;
                        }}
                        
                        .info-box strong {{
                            font-size: 14px !important;
                        }}
                        
                        .timer {{
                            font-size: 20px !important;
                        }}
                        
                        .footer {{
                            padding: 20px !important;
                        }}
                        
                        .footer p {{
                            font-size: 12px !important;
                            margin: 3px 0 !important;
                        }}
                    }}

                    @media screen and (max-width: 380px) {{
                        .header {{
                            padding: 25px 15px !important;
                        }}
                        
                        .header i {{
                            font-size: 35px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 20px !important;
                        }}
                        
                        .content {{
                            padding: 20px 15px !important;
                        }}
                        
                        .pin-box {{
                            padding: 15px !important;
                        }}
                        
                        .pin {{
                            font-size: 24px !important;
                            letter-spacing: 5px !important;
                        }}
                        
                        .info-box {{
                            padding: 12px !important;
                        }}
                        
                        .info-box p {{
                            font-size: 12px !important;
                        }}
                        
                        .timer {{
                            font-size: 18px !important;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <i class="fas fa-envelope"></i>
                        <h1>Verify Your Email</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hello <strong>{user_name}</strong>,</p>
                        
                        <p>Thank you for registering with WinPrize! Please use the following 6-digit PIN to verify your email address:</p>
                        
                        <div class="pin-box">
                            <div class="pin">{pin}</div>
                        </div>
                        
                        <div class="info-box">
                            <p><i class="fas fa-clock" style="color: #ffc107; margin-right: 8px;"></i> 
                               <strong>This PIN will expire in 20 minutes</strong></p>
                            <p><i class="fas fa-shield-alt" style="color: #28a745; margin-right: 8px;"></i> 
                               For security, never share this PIN with anyone</p>
                            <p><i class="fas fa-redo-alt" style="color: #667eea; margin-right: 8px;"></i> 
                               You can request a new PIN if this one expires</p>
                        </div>
                        
                        <p>If you didn't request this verification, please ignore this email.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 WinPrize. All rights reserved.</p>
                        <p>Lahore, Pakistan</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
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
                start_tls=True
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
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Poppins', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header i {{
                        font-size: 60px;
                        margin-bottom: 15px;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .content p {{
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 20px;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        text-decoration: none;
                        padding: 15px 40px;
                        border-radius: 50px;
                        font-weight: 600;
                        margin: 20px 0;
                        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
                    }}
                    .button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
                    }}
                    .info-box {{
                        background: #f8f9fa;
                        border-left: 4px solid #ffc107;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 30px 0;
                    }}
                    .info-box p {{
                        margin: 5px 0;
                        color: #666;
                    }}
                    .info-box .warning {{
                        color: #dc3545;
                        font-weight: 600;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #dee2e6;
                    }}
                    .footer p {{
                        color: #999;
                        margin: 5px 0;
                        font-size: 14px;
                    }}
                    .footer a {{
                        color: #667eea;
                        text-decoration: none;
                    }}
                    
              
                    @media screen and (max-width: 600px) {{
                        .container {{
                            max-width: 100% !important;
                            margin: 0 10px !important;
                        }}
                        
                        .header {{
                            padding: 30px 20px !important;
                        }}
                        
                        .header i {{
                            font-size: 40px !important;
                            margin-bottom: 10px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 22px !important;
                        }}
                        
                        .content {{
                            padding: 30px 20px !important;
                        }}
                        
                        .content p {{
                            font-size: 14px !important;
                            line-height: 1.5 !important;
                            margin-bottom: 15px !important;
                        }}
                        
                        .button {{
                            padding: 12px 30px !important;
                            font-size: 14px !important;
                            margin: 15px 0 !important;
                        }}
                        
                        .info-box {{
                            padding: 15px !important;
                            margin: 20px 0 !important;
                        }}
                        
                        .info-box p {{
                            font-size: 13px !important;
                            margin: 5px 0 !important;
                        }}
                        
                        .info-box .warning {{
                            font-size: 13px !important;
                        }}
                        
                        .footer {{
                            padding: 20px !important;
                        }}
                        
                        .footer p {{
                            font-size: 12px !important;
                            margin: 3px 0 !important;
                        }}
                        
                        .footer a {{
                            font-size: 12px !important;
                        }}
                    }}

                    @media screen and (max-width: 380px) {{
                        .header {{
                            padding: 25px 15px !important;
                        }}
                        
                        .header i {{
                            font-size: 35px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 20px !important;
                        }}
                        
                        .content {{
                            padding: 20px 15px !important;
                        }}
                        
                        .content p {{
                            font-size: 13px !important;
                            margin-bottom: 12px !important;
                        }}
                        
                        .button {{
                            padding: 10px 25px !important;
                            font-size: 13px !important;
                        }}
                        
                        .info-box {{
                            padding: 12px !important;
                        }}
                        
                        .info-box p {{
                            font-size: 12px !important;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <i class="fas fa-trophy"></i>
                        <h1>WinPrize Password Reset</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hello <strong>{user_name}</strong>,</p>
                        
                        <p>We received a request to reset your password for your WinPrize account. Click the button below to create a new password:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="button">
                                <i class="fas fa-key" style="margin-right: 10px;"></i>
                                Reset Password
                            </a>
                        </div>
                        
                        <div class="info-box">
                            <p><i class="fas fa-clock" style="color: #ffc107; margin-right: 8px;"></i> 
                               <strong>This link will expire in 1 hour</strong></p>
                            <p><i class="fas fa-shield-alt" style="color: #28a745; margin-right: 8px;"></i> 
                               For your security, this link can only be used once.</p>
                            <p class="warning"><i class="fas fa-exclamation-triangle"></i> 
                               If you didn't request this, please ignore this email.</p>
                        </div>
                        
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 12px;">
                            {reset_link}
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 WinPrize. All rights reserved.</p>
                        <p>Lahore, Pakistan</p>
                        <p>
                            <a href="#">Privacy Policy</a> | 
                            <a href="#">Terms of Service</a> | 
                            <a href="#">Contact Support</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
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
                start_tls=True
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
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Poppins', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 32px;
                        font-weight: 700;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        text-decoration: none;
                        padding: 15px 40px;
                        border-radius: 50px;
                        font-weight: 600;
                        margin: 20px 0;
                        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #dee2e6;
                    }}
                    
                                    
                    @media screen and (max-width: 600px) {{
                        .container {{
                            max-width: 100% !important;
                            margin: 0 10px !important;
                        }}
                        
                        .header {{
                            padding: 30px 20px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 24px !important;
                        }}
                        
                        .content {{
                            padding: 30px 20px !important;
                        }}
                        
                        .content p {{
                            font-size: 14px !important;
                            line-height: 1.5 !important;
                            margin-bottom: 15px !important;
                        }}
                        
                        .button {{
                            padding: 12px 30px !important;
                            font-size: 14px !important;
                            margin: 15px 0 !important;
                        }}
                        
                        .footer {{
                            padding: 20px !important;
                        }}
                        
                        .footer p {{
                            font-size: 12px !important;
                            margin: 3px 0 !important;
                        }}
                    }}

                    @media screen and (max-width: 380px) {{
                        .header {{
                            padding: 25px 15px !important;
                        }}
                        
                        .header h1 {{
                            font-size: 22px !important;
                        }}
                        
                        .content {{
                            padding: 20px 15px !important;
                        }}
                        
                        .content p {{
                            font-size: 13px !important;
                            margin-bottom: 12px !important;
                        }}
                        
                        .button {{
                            padding: 10px 25px !important;
                            font-size: 13px !important;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to WinPrize!</h1>
                    </div>
                    <div class="content">
                        <p>Hello <strong>{user_name}</strong>,</p>
                        <p>Thank you for joining WinPrize! You're now ready to participate in exciting lucky draws and win amazing prizes.</p>
                        <p>Get started by browsing our active draws:</p>
                        <p style="text-align: center;">
                            <a href="https://winprize.vercel.app/#draws" class="button">View Active Draws</a>
                        </p>
                        <p>Good luck!</p>
                    </div>
                    <div class="footer">
                        <p>© 2026 WinPrize. All rights reserved.</p>
                        <p>Lahore, Pakistan</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
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
                use_tls=True  # ← 465 کے لیے یہ استعمال کریں
            )
            # await aiosmtplib.send(
            #     message,
            #     hostname=self.smtp_host,
            #     port=self.smtp_port,
            #     username=self.smtp_user,
            #     password=self.smtp_password,
            #     start_tls=True
            # )
            
            print(f"Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            return False