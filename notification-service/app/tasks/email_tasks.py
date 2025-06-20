"""
Tâches Celery pour l'envoi d'emails
"""
from celery import current_task
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import uuid

from app.core.celery_app import celery_app
from app.services.email_service import email_service
from app.models.notification import NotificationLog, NotificationStatus, UserPreference
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(
    self,
    notification_id: str,
    to_email: str,
    subject: str,
    content: str,
    html_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    template_id: Optional[str] = None,
    template_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    notification_type: Optional[str] = None,
    priority: str = "normal"
):
    """Tâche d'envoi d'email"""
    db = SessionLocal()
    
    try:
        logger.info(f"Envoi email {notification_id} à {to_email}")
        
        # Récupérer ou créer le log de notification
        notification_log = db.query(NotificationLog).filter(
            NotificationLog.notification_id == notification_id
        ).first()
        
        if not notification_log:
            notification_log = NotificationLog(
                notification_id=notification_id,
                user_id=user_id,
                notification_type=notification_type,
                channel="email",
                priority=priority,
                subject=subject,
                content=content,
                template_id=template_id,
                template_data=template_data,
                recipient_email=to_email,
                status="pending"
            )
            db.add(notification_log)
            db.commit()
        
        # Vérifier les préférences utilisateur
        if user_id:
            user_prefs = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if user_prefs and not user_prefs.email_enabled:
                logger.info(f"Email désactivé pour l'utilisateur {user_id}")
                notification_log.status = "cancelled"
                notification_log.error_message = "Email désactivé par l'utilisateur"
                db.commit()
                return {"success": False, "reason": "email_disabled"}
        
        # Envoyer l'email (synchrone dans Celery)
        import asyncio
        result = asyncio.run(email_service.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            template_id=template_id,
            template_data=template_data
        ))
        
        # Mettre à jour le log
        if result.get("success"):
            notification_log.status = "sent"
            notification_log.sent_at = datetime.now()
            notification_log.external_id = result.get("message_id")
            notification_log.metadata = result
            logger.info(f"Email {notification_id} envoyé avec succès")
        else:
            notification_log.status = "failed"
            notification_log.failed_at = datetime.now()
            notification_log.error_message = result.get("error", "Erreur inconnue")
            notification_log.retry_count += 1
            logger.error(f"Échec envoi email {notification_id}: {result.get('error')}")
            
            # Programmer un retry si possible
            if notification_log.retry_count < notification_log.max_retries:
                retry_delay = 60 * (2 ** notification_log.retry_count)  # Backoff exponentiel
                notification_log.next_retry_at = datetime.now() + timedelta(seconds=retry_delay)
                notification_log.status = "retry"
                
                # Relancer la tâche
                raise self.retry(countdown=retry_delay)
        
        db.commit()
        return result
        
    except Exception as e:
        logger.error(f"Erreur tâche email {notification_id}: {e}")
        
        # Mettre à jour le log d'erreur
        if 'notification_log' in locals():
            notification_log.status = "failed"
            notification_log.failed_at = datetime.now()
            notification_log.error_message = str(e)
            notification_log.retry_count += 1
            db.commit()
        
        # Retry si possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        raise
    
    finally:
        db.close()


@celery_app.task
def send_bulk_emails_task(emails: List[Dict[str, Any]]):
    """Tâche d'envoi d'emails en lot"""
    try:
        logger.info(f"Envoi de {len(emails)} emails en lot")
        
        results = []
        for email_data in emails:
            # Générer un ID de notification unique
            notification_id = email_data.get("notification_id", str(uuid.uuid4()))
            
            # Lancer la tâche d'envoi individuelle
            task = send_email_task.delay(
                notification_id=notification_id,
                **email_data
            )
            
            results.append({
                "notification_id": notification_id,
                "task_id": task.id,
                "email": email_data.get("to_email")
            })
        
        logger.info(f"Lot de {len(emails)} emails programmé")
        return results
        
    except Exception as e:
        logger.error(f"Erreur envoi lot emails: {e}")
        raise


@celery_app.task
def send_daily_digest():
    """Tâche d'envoi du digest quotidien"""
    db = SessionLocal()
    
    try:
        logger.info("Envoi du digest quotidien")
        
        # Récupérer les utilisateurs qui ont activé le digest quotidien
        users_with_digest = db.query(UserPreference).filter(
            UserPreference.daily_digest == True,
            UserPreference.email_enabled == True
        ).all()
        
        for user_pref in users_with_digest:
            # TODO: Générer le contenu du digest pour cet utilisateur
            # - Résumé des absences de la journée
            # - Messages non lus
            # - Justifications en attente
            
            digest_data = {
                "user_id": user_pref.user_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "absences_count": 0,  # TODO: Calculer
                "unread_messages": 0,  # TODO: Calculer
                "pending_justifications": 0  # TODO: Calculer
            }
            
            # Envoyer le digest
            notification_id = f"daily_digest_{user_pref.user_id}_{datetime.now().strftime('%Y%m%d')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email="",  # TODO: Récupérer l'email de l'utilisateur
                subject="Digest quotidien PresencePro",
                content="",  # Sera généré par le template
                template_id="daily_digest_email_fr",
                template_data=digest_data,
                user_id=user_pref.user_id,
                notification_type="daily_digest",
                priority="low"
            )
        
        logger.info(f"Digest quotidien envoyé à {len(users_with_digest)} utilisateurs")
        
    except Exception as e:
        logger.error(f"Erreur envoi digest quotidien: {e}")
        raise
    
    finally:
        db.close()


@celery_app.task
def send_weekly_report():
    """Tâche d'envoi du rapport hebdomadaire"""
    db = SessionLocal()
    
    try:
        logger.info("Envoi du rapport hebdomadaire")
        
        # Récupérer les utilisateurs qui ont activé le rapport hebdomadaire
        users_with_report = db.query(UserPreference).filter(
            UserPreference.weekly_report == True,
            UserPreference.email_enabled == True
        ).all()
        
        for user_pref in users_with_report:
            # TODO: Générer le contenu du rapport pour cet utilisateur
            # - Statistiques de présence de la semaine
            # - Résumé des justifications
            # - Tendances et alertes
            
            report_data = {
                "user_id": user_pref.user_id,
                "week_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "week_end": datetime.now().strftime("%Y-%m-%d"),
                "attendance_rate": 95.0,  # TODO: Calculer
                "total_absences": 2,  # TODO: Calculer
                "justified_absences": 1,  # TODO: Calculer
                "unjustified_absences": 1  # TODO: Calculer
            }
            
            # Envoyer le rapport
            notification_id = f"weekly_report_{user_pref.user_id}_{datetime.now().strftime('%Y%W')}"
            
            send_email_task.delay(
                notification_id=notification_id,
                to_email="",  # TODO: Récupérer l'email de l'utilisateur
                subject="Rapport hebdomadaire PresencePro",
                content="",  # Sera généré par le template
                template_id="weekly_report_email_fr",
                template_data=report_data,
                user_id=user_pref.user_id,
                notification_type="weekly_report",
                priority="low"
            )
        
        logger.info(f"Rapport hebdomadaire envoyé à {len(users_with_report)} utilisateurs")
        
    except Exception as e:
        logger.error(f"Erreur envoi rapport hebdomadaire: {e}")
        raise
    
    finally:
        db.close()


@celery_app.task
def retry_failed_emails():
    """Tâche de retry des emails échoués"""
    db = SessionLocal()
    
    try:
        logger.info("Retry des emails échoués")
        
        # Récupérer les emails en attente de retry
        failed_notifications = db.query(NotificationLog).filter(
            NotificationLog.status == "retry",
            NotificationLog.next_retry_at <= datetime.now(),
            NotificationLog.retry_count < NotificationLog.max_retries
        ).all()
        
        for notification in failed_notifications:
            # Relancer la tâche d'envoi
            send_email_task.delay(
                notification_id=notification.notification_id,
                to_email=notification.recipient_email,
                subject=notification.subject,
                content=notification.content,
                template_id=notification.template_id,
                template_data=notification.template_data,
                user_id=notification.user_id,
                notification_type=notification.notification_type,
                priority=notification.priority
            )
        
        logger.info(f"{len(failed_notifications)} emails relancés")
        
    except Exception as e:
        logger.error(f"Erreur retry emails: {e}")
        raise
    
    finally:
        db.close()
