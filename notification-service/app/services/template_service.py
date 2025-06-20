"""
Service de gestion des templates de notifications
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.core.database import get_database
from app.models.notification import NotificationTemplate, NotificationType, NotificationChannel

logger = logging.getLogger(__name__)


class TemplateService:
    """Service de gestion des templates"""
    
    def __init__(self):
        pass
    
    async def get_template(
        self,
        template_id: str,
        db: Session = None
    ) -> Optional[NotificationTemplate]:
        """Récupérer un template par ID"""
        if not db:
            db = next(get_database())
        
        try:
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.template_id == template_id,
                NotificationTemplate.is_active == True
            ).first()
            
            return template
            
        except Exception as e:
            logger.error(f"Erreur récupération template {template_id}: {e}")
            return None
        finally:
            if not db:
                db.close()
    
    async def get_default_template(
        self,
        notification_type: NotificationType,
        channel: NotificationChannel,
        language: str = "fr",
        db: Session = None
    ) -> Optional[NotificationTemplate]:
        """Récupérer le template par défaut pour un type et canal"""
        if not db:
            db = next(get_database())
        
        try:
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.notification_type == notification_type.value,
                NotificationTemplate.channel == channel.value,
                NotificationTemplate.language == language,
                NotificationTemplate.is_active == True,
                NotificationTemplate.is_default == True
            ).first()
            
            # Si pas de template par défaut, prendre le premier disponible
            if not template:
                template = db.query(NotificationTemplate).filter(
                    NotificationTemplate.notification_type == notification_type.value,
                    NotificationTemplate.channel == channel.value,
                    NotificationTemplate.language == language,
                    NotificationTemplate.is_active == True
                ).first()
            
            return template
            
        except Exception as e:
            logger.error(f"Erreur récupération template par défaut: {e}")
            return None
        finally:
            if not db:
                db.close()
    
    async def create_template(
        self,
        template_data: Dict[str, Any],
        db: Session = None
    ) -> Optional[NotificationTemplate]:
        """Créer un nouveau template"""
        if not db:
            db = next(get_database())
        
        try:
            template = NotificationTemplate(**template_data)
            db.add(template)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Template créé: {template.template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Erreur création template: {e}")
            db.rollback()
            return None
        finally:
            if not db:
                db.close()
    
    async def update_template(
        self,
        template_id: str,
        template_data: Dict[str, Any],
        db: Session = None
    ) -> Optional[NotificationTemplate]:
        """Mettre à jour un template"""
        if not db:
            db = next(get_database())
        
        try:
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.template_id == template_id
            ).first()
            
            if not template:
                return None
            
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            db.commit()
            db.refresh(template)
            
            logger.info(f"Template mis à jour: {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Erreur mise à jour template {template_id}: {e}")
            db.rollback()
            return None
        finally:
            if not db:
                db.close()
    
    async def delete_template(
        self,
        template_id: str,
        db: Session = None
    ) -> bool:
        """Supprimer un template (désactivation)"""
        if not db:
            db = next(get_database())
        
        try:
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.template_id == template_id
            ).first()
            
            if not template:
                return False
            
            template.is_active = False
            db.commit()
            
            logger.info(f"Template désactivé: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression template {template_id}: {e}")
            db.rollback()
            return False
        finally:
            if not db:
                db.close()
    
    async def list_templates(
        self,
        notification_type: Optional[NotificationType] = None,
        channel: Optional[NotificationChannel] = None,
        language: Optional[str] = None,
        active_only: bool = True,
        db: Session = None
    ) -> List[NotificationTemplate]:
        """Lister les templates avec filtres"""
        if not db:
            db = next(get_database())
        
        try:
            query = db.query(NotificationTemplate)
            
            if notification_type:
                query = query.filter(
                    NotificationTemplate.notification_type == notification_type.value
                )
            
            if channel:
                query = query.filter(
                    NotificationTemplate.channel == channel.value
                )
            
            if language:
                query = query.filter(
                    NotificationTemplate.language == language
                )
            
            if active_only:
                query = query.filter(
                    NotificationTemplate.is_active == True
                )
            
            templates = query.order_by(
                NotificationTemplate.notification_type,
                NotificationTemplate.channel,
                NotificationTemplate.language
            ).all()
            
            return templates
            
        except Exception as e:
            logger.error(f"Erreur listage templates: {e}")
            return []
        finally:
            if not db:
                db.close()
    
    async def initialize_default_templates(self, db: Session = None):
        """Initialiser les templates par défaut"""
        if not db:
            db = next(get_database())
        
        try:
            # Templates par défaut pour les absences
            default_templates = [
                {
                    "template_id": "absence_detected_email_fr",
                    "name": "Absence détectée - Email",
                    "description": "Notification d'absence détectée",
                    "notification_type": "absence_detected",
                    "channel": "email",
                    "language": "fr",
                    "subject_template": "Absence détectée - {{ student_name }}",
                    "content_template": """Bonjour {{ parent_name }},

Nous vous informons qu'une absence a été détectée pour {{ student_name }} le {{ absence_date }} à {{ absence_time }}.

Cours concerné : {{ course_name }}
Enseignant : {{ teacher_name }}

Si cette absence est justifiée, vous pouvez soumettre une justification via l'application PresencePro.

Cordialement,
L'équipe PresencePro""",
                    "html_template": """<h2>Absence détectée</h2>
<p>Bonjour <strong>{{ parent_name }}</strong>,</p>
<p>Nous vous informons qu'une absence a été détectée pour <strong>{{ student_name }}</strong> le {{ absence_date }} à {{ absence_time }}.</p>
<ul>
<li><strong>Cours concerné :</strong> {{ course_name }}</li>
<li><strong>Enseignant :</strong> {{ teacher_name }}</li>
</ul>
<p>Si cette absence est justifiée, vous pouvez soumettre une justification via l'application PresencePro.</p>
<p>Cordialement,<br>L'équipe PresencePro</p>""",
                    "is_active": True,
                    "is_default": True,
                    "variables": {
                        "student_name": "Nom de l'étudiant",
                        "parent_name": "Nom du parent",
                        "absence_date": "Date de l'absence",
                        "absence_time": "Heure de l'absence",
                        "course_name": "Nom du cours",
                        "teacher_name": "Nom de l'enseignant"
                    }
                },
                {
                    "template_id": "justification_approved_email_fr",
                    "name": "Justification approuvée - Email",
                    "description": "Notification de justification approuvée",
                    "notification_type": "justification_approved",
                    "channel": "email",
                    "language": "fr",
                    "subject_template": "Justification approuvée - {{ student_name }}",
                    "content_template": """Bonjour {{ parent_name }},

Nous vous informons que la justification d'absence pour {{ student_name }} a été approuvée.

Détails de la justification :
- Titre : {{ justification_title }}
- Période : du {{ start_date }} au {{ end_date }}
- Statut : Approuvée

Merci pour votre collaboration.

Cordialement,
L'équipe PresencePro""",
                    "html_template": """<h2>Justification approuvée</h2>
<p>Bonjour <strong>{{ parent_name }}</strong>,</p>
<p>Nous vous informons que la justification d'absence pour <strong>{{ student_name }}</strong> a été approuvée.</p>
<h3>Détails de la justification :</h3>
<ul>
<li><strong>Titre :</strong> {{ justification_title }}</li>
<li><strong>Période :</strong> du {{ start_date }} au {{ end_date }}</li>
<li><strong>Statut :</strong> <span style="color: green;">Approuvée</span></li>
</ul>
<p>Merci pour votre collaboration.</p>
<p>Cordialement,<br>L'équipe PresencePro</p>""",
                    "is_active": True,
                    "is_default": True,
                    "variables": {
                        "student_name": "Nom de l'étudiant",
                        "parent_name": "Nom du parent",
                        "justification_title": "Titre de la justification",
                        "start_date": "Date de début",
                        "end_date": "Date de fin"
                    }
                },
                {
                    "template_id": "message_received_email_fr",
                    "name": "Message reçu - Email",
                    "description": "Notification de nouveau message",
                    "notification_type": "message_received",
                    "channel": "email",
                    "language": "fr",
                    "subject_template": "Nouveau message de {{ sender_name }}",
                    "content_template": """Bonjour {{ recipient_name }},

Vous avez reçu un nouveau message de {{ sender_name }}.

Message : {{ message_content }}

Vous pouvez répondre directement via l'application PresencePro.

Cordialement,
L'équipe PresencePro""",
                    "html_template": """<h2>Nouveau message</h2>
<p>Bonjour <strong>{{ recipient_name }}</strong>,</p>
<p>Vous avez reçu un nouveau message de <strong>{{ sender_name }}</strong>.</p>
<blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin: 10px 0;">
{{ message_content }}
</blockquote>
<p>Vous pouvez répondre directement via l'application PresencePro.</p>
<p>Cordialement,<br>L'équipe PresencePro</p>""",
                    "is_active": True,
                    "is_default": True,
                    "variables": {
                        "recipient_name": "Nom du destinataire",
                        "sender_name": "Nom de l'expéditeur",
                        "message_content": "Contenu du message"
                    }
                }
            ]
            
            # Créer les templates s'ils n'existent pas
            for template_data in default_templates:
                existing = db.query(NotificationTemplate).filter(
                    NotificationTemplate.template_id == template_data["template_id"]
                ).first()
                
                if not existing:
                    template = NotificationTemplate(**template_data)
                    db.add(template)
                    logger.info(f"Template par défaut créé: {template_data['template_id']}")
            
            db.commit()
            logger.info("Templates par défaut initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation templates par défaut: {e}")
            db.rollback()
        finally:
            if not db:
                db.close()


# Instance globale du service template
template_service = TemplateService()
