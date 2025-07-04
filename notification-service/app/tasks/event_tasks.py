"""
Tâches Celery pour le traitement des événements
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import uuid

from app.core.celery_app import celery_app
from app.tasks.email_tasks import send_email_task
from app.models.notification import EventQueue, NotificationLog
from app.core.database import SessionLocal, Session # Ajout de Session pour le type hint
# Supposons que les modèles User et Parent existent
from app.models.user import User, Parent # À adapter selon la structure réelle

logger = logging.getLogger(__name__)

# Placeholder functions - these need proper implementation
def get_student_and_parent_info(student_id: str, db: Session) -> Dict[str, Any]:
    """Récupère les informations de l'étudiant et de ses parents. À IMPLÉMENTER."""
    # Cette fonction devrait interagir avec le user-service ou les tables User/Parent.
    logger.info(f"Récupération des informations pour l'étudiant {student_id} (simulation).")
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        logger.warning(f"Étudiant {student_id} non trouvé.")
        return {}

    parents_info = []
    # Supposons une relation student.parents ou une table d'association
    # Ceci est un exemple très simplifié
    # parents = db.query(Parent).join(Parent.children).filter(User.id == student_id).all()
    # Mieux: Supposer une table `StudentParentAssociation`
    # ou que le modèle `User` a un champ `parent_ids` ou une relation.
    # Pour la simulation, on retourne des données fixes si l'étudiant est trouvé.

    # Exemple de récupération si les parents sont directement liés à l'étudiant (simplifié)
    # parents = db.query(User).filter(User.role == "parent", User.children.any(id=student_id)).all()
    # Cela dépend fortement du schéma de la base de données.

    # Simulation:
    parent_emails = [f"parent_of_{student_id}@example.com"] # Email de parent simulé

    return {
        "student_name": student.full_name if hasattr(student, 'full_name') else f"Student {student_id}",
        "parent_name": f"Parent of {student.full_name}" if hasattr(student, 'full_name') else f"Parent of Student {student_id}", # Simplifié
        "parent_emails": parent_emails, # Pourrait être une liste d'emails
    }

def validate_webhook_signature(payload: Dict[str, Any], headers: Optional[Dict[str, str]]) -> bool:
    """Valide la signature d'un webhook. À IMPLÉMENTER."""
    # Implémenter la logique de validation de signature ici (ex: HMAC SHA256)
    # Cela dépendra du service envoyant le webhook (ex: GitHub, Stripe, etc.)
    # Pour l'instant, on suppose que c'est valide pour les tests.
    if headers and headers.get("X-Webhook-Secret"): # Exemple de header
        # secret = os.getenv("WEBHOOK_SECRET")
        # signature = headers.get("X-Hub-Signature-256") # Exemple
        # if not signature or not verify_signature(payload, secret, signature):
        #     return False
        pass # Laisser la logique de validation pour plus tard
    logger.warning("Validation de signature du webhook non implémentée, autorisant par défaut.")
    return True


@celery_app.task
def process_event(event_data: Dict[str, Any]):
    """Traiter un événement et déclencher les notifications appropriées"""
    db = SessionLocal()
    
    try:
        event_type = event_data.get("event_type")
        source_service = event_data.get("source_service")
        data = event_data.get("data", {})
        
        logger.info(f"Traitement événement {event_type} de {source_service}")
        
        # Enregistrer l'événement dans la queue
        event_id = str(uuid.uuid4())
        event_queue = EventQueue(
            event_id=event_id,
            source_service=source_service,
            event_type=event_type,
            event_data=data,
            status="processing"
        )
        db.add(event_queue)
        db.commit()
        
        # Traiter selon le type d'événement
        if event_type == "absence_detected":
            process_absence_detected(data, db)
        elif event_type == "justification_submitted":
            process_justification_submitted(data, db)
        elif event_type == "justification_approved":
            process_justification_approved(data, db)
        elif event_type == "justification_rejected":
            process_justification_rejected(data, db)
        elif event_type == "message_received":
            process_message_received(data, db)
        elif event_type == "parent_approval_required":
            process_parent_approval_required(data, db)
        elif event_type == "admin_validation_required":
            process_admin_validation_required(data, db)
        else:
            logger.warning(f"Type d'événement non géré: {event_type}")
        
        # Marquer l'événement comme traité
        event_queue.status = "processed"
        event_queue.processed_at = datetime.now()
        db.commit()
        
        logger.info(f"Événement {event_type} traité avec succès")
        
    except Exception as e:
        logger.error(f"Erreur traitement événement: {e}")
        
        # Marquer l'événement comme échoué
        if 'event_queue' in locals():
            event_queue.status = "failed"
            event_queue.error_message = str(e)
            event_queue.retry_count += 1
            db.commit()
        
        raise
    
    finally:
        db.close()


def process_absence_detected(data: Dict[str, Any], db):
    """Traiter une absence détectée"""
    try:
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        absence_date = data.get("absence_date")
        absence_time = data.get("absence_time")
        
        # Récupérer les informations de l'étudiant et des parents
        user_info = get_student_and_parent_info(student_id, db)
        
        student_name = user_info.get("student_name", "Étudiant")
        parent_name = user_info.get("parent_name", "Parent")
        parent_emails = user_info.get("parent_emails", [])

        # Données pour le template
        template_data = {
            "student_name": student_name,
            "parent_name": parent_name,
            "absence_date": absence_date,
            "absence_time": absence_time,
            "course_name": data.get("course_name", "Cours"),
            "teacher_name": data.get("teacher_name", "Enseignant")
        }
        
        # Envoyer notification aux parents
        if not parent_emails:
            logger.warning(f"Aucun email de parent trouvé pour l'étudiant {student_id} lors de la détection d'absence.")

        for parent_email in parent_emails:
            notification_id = f"absence_{student_id}_{course_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email=parent_email,
                subject="",  # Sera généré par le template
                content="",  # Sera généré par le template
                template_id="absence_detected_email_fr",
                template_data=template_data,
                user_id=student_id,
                notification_type="absence_detected",
                priority="high"
            )
        
        logger.info(f"Notifications d'absence envoyées pour {student_id}")
        
    except Exception as e:
        logger.error(f"Erreur traitement absence détectée: {e}")
        raise


def process_justification_submitted(data: Dict[str, Any], db):
    """Traiter une justification soumise"""
    try:
        justification_id = data.get("justification_id")
        student_id = data.get("student_id")
        
        # Données pour le template
        template_data = {
            "student_name": data.get("student_name", "Étudiant"),
            "justification_title": data.get("title", "Justification"),
            "justification_description": data.get("description", ""),
            "submission_date": data.get("submitted_at", datetime.now().isoformat())
        }
        
        # Notifier les parents si approbation requise
        if data.get("parent_approval_required"):
            parent_emails = data.get("parent_emails", [])
            for parent_email in parent_emails:
                notification_id = f"justification_submitted_{justification_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                send_email_task.delay(
                    notification_id=notification_id,
                    to_email=parent_email,
                    subject="",
                    content="",
                    template_id="parent_approval_required_email_fr",
                    template_data=template_data,
                    user_id=student_id,
                    notification_type="parent_approval_required",
                    priority="normal"
                )
        
        # Notifier les administrateurs si validation requise
        if data.get("admin_validation_required"):
            admin_emails = data.get("admin_emails", [])
            for admin_email in admin_emails:
                notification_id = f"justification_admin_{justification_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                send_email_task.delay(
                    notification_id=notification_id,
                    to_email=admin_email,
                    subject="",
                    content="",
                    template_id="admin_validation_required_email_fr",
                    template_data=template_data,
                    user_id=student_id,
                    notification_type="admin_validation_required",
                    priority="normal"
                )
        
        logger.info(f"Notifications de justification soumise envoyées pour {justification_id}")
        
    except Exception as e:
        logger.error(f"Erreur traitement justification soumise: {e}")
        raise


def process_justification_approved(data: Dict[str, Any], db):
    """Traiter une justification approuvée"""
    try:
        justification_id = data.get("justification_id")
        student_id = data.get("student_id")
        
        # Données pour le template
        template_data = {
            "student_name": data.get("student_name", "Étudiant"),
            "parent_name": data.get("parent_name", "Parent"),
            "justification_title": data.get("title", "Justification"),
            "start_date": data.get("absence_start_date", ""),
            "end_date": data.get("absence_end_date", ""),
            "approved_by": data.get("approved_by", "Administration"),
            "approved_at": data.get("approved_at", datetime.now().isoformat())
        }
        
        # Notifier l'étudiant et les parents
        recipient_emails = data.get("recipient_emails", [])
        for email in recipient_emails:
            notification_id = f"justification_approved_{justification_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email=email,
                subject="",
                content="",
                template_id="justification_approved_email_fr",
                template_data=template_data,
                user_id=student_id,
                notification_type="justification_approved",
                priority="normal"
            )
        
        logger.info(f"Notifications de justification approuvée envoyées pour {justification_id}")
        
    except Exception as e:
        logger.error(f"Erreur traitement justification approuvée: {e}")
        raise


def process_justification_rejected(data: Dict[str, Any], db):
    """Traiter une justification rejetée"""
    try:
        justification_id = data.get("justification_id")
        student_id = data.get("student_id")
        
        # Données pour le template
        template_data = {
            "student_name": data.get("student_name", "Étudiant"),
            "parent_name": data.get("parent_name", "Parent"),
            "justification_title": data.get("title", "Justification"),
            "rejection_reason": data.get("rejection_reason", "Non spécifiée"),
            "rejected_by": data.get("rejected_by", "Administration"),
            "rejected_at": data.get("rejected_at", datetime.now().isoformat())
        }
        
        # Notifier l'étudiant et les parents
        recipient_emails = data.get("recipient_emails", [])
        for email in recipient_emails:
            notification_id = f"justification_rejected_{justification_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email=email,
                subject="",
                content="",
                template_id="justification_rejected_email_fr",
                template_data=template_data,
                user_id=student_id,
                notification_type="justification_rejected",
                priority="high"
            )
        
        logger.info(f"Notifications de justification rejetée envoyées pour {justification_id}")
        
    except Exception as e:
        logger.error(f"Erreur traitement justification rejetée: {e}")
        raise


def process_message_received(data: Dict[str, Any], db):
    """Traiter un message reçu"""
    try:
        message_id = data.get("message_id")
        sender_id = data.get("sender_id")
        recipient_id = data.get("recipient_id")
        
        # Données pour le template
        template_data = {
            "recipient_name": data.get("recipient_name", "Utilisateur"),
            "sender_name": data.get("sender_name", "Expéditeur"),
            "message_content": data.get("content", ""),
            "sent_at": data.get("sent_at", datetime.now().isoformat())
        }
        
        # Notifier le destinataire
        recipient_email = data.get("recipient_email")
        if recipient_email:
            notification_id = f"message_received_{message_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email=recipient_email,
                subject="",
                content="",
                template_id="message_received_email_fr",
                template_data=template_data,
                user_id=recipient_id,
                notification_type="message_received",
                priority="normal"
            )
        
        logger.info(f"Notification de message reçu envoyée pour {message_id}")
        
    except Exception as e:
        logger.error(f"Erreur traitement message reçu: {e}")
        raise


def process_parent_approval_required(data: Dict[str, Any], db):
    """Traiter une demande d'approbation parentale"""
    process_justification_submitted(data, db)


def process_admin_validation_required(data: Dict[str, Any], db):
    """Traiter une demande de validation administrative"""
    process_justification_submitted(data, db)


@celery_app.task
def cleanup_old_notifications():
    """Nettoyer les anciennes notifications"""
    db = SessionLocal()
    
    try:
        logger.info("Nettoyage des anciennes notifications")
        
        # Supprimer les logs de notifications de plus de 90 jours
        cutoff_date = datetime.now() - timedelta(days=90)
        
        deleted_logs = db.query(NotificationLog).filter(
            NotificationLog.created_at < cutoff_date
        ).delete()
        
        # Supprimer les événements traités de plus de 30 jours
        event_cutoff_date = datetime.now() - timedelta(days=30)
        
        deleted_events = db.query(EventQueue).filter(
            EventQueue.created_at < event_cutoff_date,
            EventQueue.status.in_(["processed", "failed"])
        ).delete()
        
        db.commit()
        
        logger.info(f"Nettoyage terminé: {deleted_logs} logs et {deleted_events} événements supprimés")
        
    except Exception as e:
        logger.error(f"Erreur nettoyage: {e}")
        raise
    
    finally:
        db.close()


@celery_app.task
def process_webhook_event(webhook_data: Dict[str, Any]):
    """Traiter un événement webhook"""
    try:
        logger.info(f"Traitement webhook: {webhook_data.get('event_type')}")
        
        # Valider la signature du webhook
        if not validate_webhook_signature(webhook_data, headers=webhook_data.get("headers")):
            logger.error("Validation de signature du webhook échouée.")
            # Pourrait lever une exception ou simplement retourner pour ignorer.
            # Pour l'instant, on logue et on continue, mais en production, il faudrait être plus strict.
            # raise HTTPException(status_code=400, detail="Invalid signature")
            return {"success": False, "reason": "invalid_signature"}

        # Extraire les données pertinentes de l'événement webhook si nécessaire
        # Par exemple, si les données de l'événement sont imbriquées
        actual_event_data = webhook_data.get("payload", webhook_data) # Supposons que les données sont dans "payload" ou à la racine
        
        # Traiter l'événement
        process_event.delay(actual_event_data)
        
        logger.info("Webhook traité avec succès")
        
    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        raise
