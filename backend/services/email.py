from pydantic import EmailStr
from ..config import email_settings
from fastapi_mail import FastMail,ConnectionConfig , MessageSchema, MessageType
from ..utils import template_directory

class EmailService:
    def __init__(self):
        self.fastemil = FastMail(ConnectionConfig(
                                    **email_settings.model_dump(),
                                    TEMPLATE_FOLDER=str(template_directory)
                                ))
        
    async def send_message(self, recipients: list[EmailStr], 
                           subject: str, context: dict, template_name: str):
        await  self.fastemil.send_message(
                    message=MessageSchema(  subject=subject,
                                            recipients=recipients,
                                            template_body=context,
                                            subtype=MessageType.html
                                            
                                        ),
                            template_name=template_name
                    
            
                )