"""
Service d'envoi d'emails
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import json

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader, Template
from premailer import transform

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service d'envoi d'emails"""
    
    def __init__(self):
        self.settings = settings
        self.template_env = Environment(
            loader=FileSystemLoader(settings.template_dir)
        )
        
        # Initialiser SendGrid si configuré
        if settings.use_sendgrid and settings.sendgrid_api_key:
            self.sendgrid_client = sendgrid.SendGridAPIClient(
                api_key=settings.sendgrid_api_key
            )
        else:
            self.sendgrid_client = None
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Envoyer un email"""
        try:
            # Utiliser les valeurs par défaut si non spécifiées
            from_email = from_email or settings.email_from
            from_name = from_name or settings.email_from_name
            
            # Rendu du template si spécifié
            if template_id and template_data:
                rendered = await self.render_template(template_id, template_data)
                if rendered:
                    subject = rendered.get("subject", subject)
                    content = rendered.get("content", content)
                    html_content = rendered.get("html_content", html_content)
            
            # Mode développement - sauvegarder dans un fichier
            if settings.mock_email_sending or settings.save_emails_to_file:
                result = await self._save_email_to_file(
                    to_email, subject, content, html_content, from_email, from_name
                )
                if settings.mock_email_sending:
                    return result
            
            # Envoi via SendGrid
            if self.sendgrid_client:
                return await self._send_via_sendgrid(
                    to_email, subject, content, html_content, 
                    from_email, from_name, attachments
                )
            
            # Envoi via SMTP
            else:
                return await self._send_via_smtp(
                    to_email, subject, content, html_content,
                    from_email, from_name, attachments
                )
                
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        from_email: str = None,
        from_name: str = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Envoyer via SendGrid"""
        try:
            from_email_obj = Email(from_email, from_name)
            to_email_obj = To(to_email)
            
            # Contenu principal (texte)
            content_obj = Content("text/plain", content)
            
            # Créer le mail
            mail = Mail(from_email_obj, to_email_obj, subject, content_obj)
            
            # Ajouter le contenu HTML si disponible
            if html_content:
                mail.add_content(Content("text/html", html_content))
            
            # Ajouter les pièces jointes
            if attachments:
                for attachment in attachments:
                    # TODO: Implémenter les pièces jointes SendGrid
                    pass
            
            # Envoyer
            response = self.sendgrid_client.send(mail)
            
            logger.info(f"Email envoyé via SendGrid à {to_email}: {response.status_code}")
            
            return {
                "success": True,
                "provider": "sendgrid",
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id"),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erreur SendGrid: {e}")
            raise
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        from_email: str = None,
        from_name: str = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Envoyer via SMTP"""
        try:
            # Créer le message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
            msg["To"] = to_email
            
            # Ajouter le contenu texte
            text_part = MIMEText(content, "plain", "utf-8")
            msg.attach(text_part)
            
            # Ajouter le contenu HTML si disponible
            if html_content:
                html_part = MIMEText(html_content, "html", "utf-8")
                msg.attach(html_part)
            
            # Ajouter les pièces jointes
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Connexion SMTP
            if settings.smtp_use_ssl:
                server = smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port)
            else:
                server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
                if settings.smtp_use_tls:
                    server.starttls()
            
            # Authentification
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            
            # Envoyer
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email envoyé via SMTP à {to_email}")
            
            return {
                "success": True,
                "provider": "smtp",
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erreur SMTP: {e}")
            raise
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Ajouter une pièce jointe"""
        try:
            filename = attachment.get("filename")
            filepath = attachment.get("filepath")
            content = attachment.get("content")
            
            if filepath and os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
            elif content:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(content)
            else:
                return
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}"
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Erreur ajout pièce jointe: {e}")
    
    async def _save_email_to_file(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        from_email: str = None,
        from_name: str = None
    ) -> Dict[str, Any]:
        """Sauvegarder l'email dans un fichier (mode développement)"""
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(settings.email_output_dir, exist_ok=True)
            
            # Nom du fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{timestamp}_{to_email.replace('@', '_at_')}.json"
            filepath = os.path.join(settings.email_output_dir, filename)
            
            # Données de l'email
            email_data = {
                "to": to_email,
                "from": from_email,
                "from_name": from_name,
                "subject": subject,
                "content": content,
                "html_content": html_content,
                "timestamp": datetime.now().isoformat(),
                "mock_mode": settings.mock_email_sending
            }
            
            # Sauvegarder
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(email_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Email sauvegardé: {filepath}")
            
            return {
                "success": True,
                "provider": "file",
                "filepath": filepath,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde email: {e}")
            raise
    
    async def render_template(
        self,
        template_id: str,
        template_data: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """Rendre un template d'email"""
        try:
            # Charger le template depuis la base de données
            from app.services.template_service import TemplateService
            template_service = TemplateService()
            
            template = await template_service.get_template(template_id)
            if not template:
                logger.warning(f"Template non trouvé: {template_id}")
                return None
            
            # Rendre le sujet
            subject = ""
            if template.subject_template:
                subject_tmpl = Template(template.subject_template)
                subject = subject_tmpl.render(**template_data)
            
            # Rendre le contenu texte
            content = ""
            if template.content_template:
                content_tmpl = Template(template.content_template)
                content = content_tmpl.render(**template_data)
            
            # Rendre le contenu HTML
            html_content = None
            if template.html_template:
                html_tmpl = Template(template.html_template)
                html_content = html_tmpl.render(**template_data)
                
                # Inliner le CSS avec premailer
                html_content = transform(html_content)
            
            return {
                "subject": subject,
                "content": content,
                "html_content": html_content
            }
            
        except Exception as e:
            logger.error(f"Erreur rendu template {template_id}: {e}")
            return None
    
    async def send_bulk_emails(
        self,
        emails: List[Dict[str, Any]],
        batch_size: int = None
    ) -> List[Dict[str, Any]]:
        """Envoyer des emails en lot"""
        batch_size = batch_size or settings.batch_size
        results = []
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            
            for email_data in batch:
                result = await self.send_email(**email_data)
                results.append(result)
        
        return results
    
    def validate_email(self, email: str) -> bool:
        """Valider une adresse email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


# Instance globale du service email
email_service = EmailService()
