"""
Script d'initialisation de la base de données pour le service de cours
"""
import sys
import os
from datetime import date, time, timedelta

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base
from app.models.course import Course, Schedule, CourseAssignment, DayOfWeek, CourseStatus, AssignmentType


def create_tables():
    """Créer les tables de la base de données"""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")


def create_sample_data():
    """Créer des données d'exemple"""
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si des données existent déjà
        if db.query(Course).first():
            print("⚠️  Des données existent déjà dans la base")
            return
        
        # Créer des cours d'exemple
        courses_data = [
            {
                "name": "Mathématiques Avancées",
                "code": "MATH001",
                "description": "Cours de mathématiques niveau 6ème",
                "subject": "Mathématiques",
                "level": "6ème",
                "credits": 3,
                "max_students": 25,
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            },
            {
                "name": "Sciences Physiques",
                "code": "PHYS001",
                "description": "Introduction aux sciences physiques",
                "subject": "Physique",
                "level": "6ème",
                "credits": 2,
                "max_students": 30,
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            },
            {
                "name": "Français Littérature",
                "code": "FRAN001",
                "description": "Étude de la littérature française",
                "subject": "Français",
                "level": "5ème",
                "credits": 4,
                "max_students": 28,
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            },
            {
                "name": "Histoire Géographie",
                "code": "HIST001",
                "description": "Histoire et géographie du monde",
                "subject": "Histoire",
                "level": "5ème",
                "credits": 3,
                "max_students": 30,
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            }
        ]
        
        courses = []
        for course_data in courses_data:
            course = Course(**course_data)
            db.add(course)
            courses.append(course)
        
        db.commit()
        print("✅ Cours créés avec succès")
        
        # Créer des emplois du temps d'exemple
        schedules_data = [
            # Mathématiques - Lundi et Mercredi
            {
                "course_id": 1,
                "day_of_week": DayOfWeek.MONDAY,
                "start_time": time(8, 0),
                "end_time": time(9, 30),
                "room": "A101",
                "building": "Bâtiment A",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            },
            {
                "course_id": 1,
                "day_of_week": DayOfWeek.WEDNESDAY,
                "start_time": time(10, 0),
                "end_time": time(11, 30),
                "room": "A101",
                "building": "Bâtiment A",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            },
            # Sciences Physiques - Mardi et Jeudi
            {
                "course_id": 2,
                "day_of_week": DayOfWeek.TUESDAY,
                "start_time": time(14, 0),
                "end_time": time(15, 30),
                "room": "B201",
                "building": "Bâtiment B",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            },
            {
                "course_id": 2,
                "day_of_week": DayOfWeek.THURSDAY,
                "start_time": time(14, 0),
                "end_time": time(15, 30),
                "room": "B201",
                "building": "Bâtiment B",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            },
            # Français - Lundi, Mercredi, Vendredi
            {
                "course_id": 3,
                "day_of_week": DayOfWeek.MONDAY,
                "start_time": time(9, 45),
                "end_time": time(11, 15),
                "room": "C301",
                "building": "Bâtiment C",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            },
            {
                "course_id": 3,
                "day_of_week": DayOfWeek.FRIDAY,
                "start_time": time(8, 0),
                "end_time": time(9, 30),
                "room": "C301",
                "building": "Bâtiment C",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31)
            }
        ]
        
        for schedule_data in schedules_data:
            schedule = Schedule(**schedule_data)
            db.add(schedule)
        
        db.commit()
        print("✅ Emplois du temps créés avec succès")
        
        # Créer des attributions d'exemple
        assignments_data = [
            # Enseignants
            {
                "course_id": 1,
                "user_id": "teacher1",
                "assignment_type": AssignmentType.TEACHER,
                "is_primary": True,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 2,
                "user_id": "teacher2",
                "assignment_type": AssignmentType.TEACHER,
                "is_primary": True,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 3,
                "user_id": "teacher1",
                "assignment_type": AssignmentType.TEACHER,
                "is_primary": True,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 4,
                "user_id": "teacher2",
                "assignment_type": AssignmentType.TEACHER,
                "is_primary": True,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            # Étudiants
            {
                "course_id": 1,
                "user_id": "student1",
                "assignment_type": AssignmentType.STUDENT,
                "is_primary": False,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 1,
                "user_id": "student2",
                "assignment_type": AssignmentType.STUDENT,
                "is_primary": False,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 2,
                "user_id": "student1",
                "assignment_type": AssignmentType.STUDENT,
                "is_primary": False,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            },
            {
                "course_id": 3,
                "user_id": "student3",
                "assignment_type": AssignmentType.STUDENT,
                "is_primary": False,
                "valid_from": date(2023, 9, 1),
                "valid_to": date(2024, 6, 30)
            }
        ]
        
        for assignment_data in assignments_data:
            assignment = CourseAssignment(**assignment_data)
            db.add(assignment)
        
        db.commit()
        print("✅ Attributions créées avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données d'exemple: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation du service de cours PresencePro")
    print("=" * 60)
    print(f"📊 Base de données: {settings.database_url}")
    
    try:
        print("\n🔧 Création des tables...")
        create_tables()
        
        print("\n👥 Création de données d'exemple...")
        create_sample_data()
        
        print("\n🎉 Initialisation terminée avec succès!")
        print("\n📝 Prochaines étapes:")
        print("   1. Lancez le service: uvicorn app.main:app --reload --port 8003")
        print("   2. Testez l'API: http://localhost:8003/docs")
        print("   3. Utilisez les tokens du service d'authentification")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
