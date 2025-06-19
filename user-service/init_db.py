"""
Script d'initialisation de la base de données pour le service utilisateur
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.models.user import Student, Teacher, Parent, ParentStudentRelation
from app.schemas.user import StudentCreate, TeacherCreate, ParentCreate, ParentStudentRelationCreate
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService
from app.services.parent_service import ParentService
from app.core.config import settings


def init_database():
    """Initialise la base de données avec des données d'exemple"""
    print("🚀 Initialisation du service utilisateur PresencePro")
    print("=" * 60)
    print(f"📊 Base de données: {settings.database_url}")
    print()
    
    try:
        # Créer les tables
        print("🔧 Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès")
        
        # Créer une session
        db = SessionLocal()
        
        try:
            # Créer des utilisateurs d'exemple
            print("👥 Création d'utilisateurs d'exemple...")
            
            # Services
            student_service = StudentService(db)
            teacher_service = TeacherService(db)
            parent_service = ParentService(db)
            
            # Créer des enseignants
            teachers_data = [
                {
                    "user_id": "teacher1",
                    "employee_number": "EMP001",
                    "first_name": "Marie",
                    "last_name": "Dupont",
                    "email": "marie.dupont@presencepro.com",
                    "phone": "0123456789",
                    "department": "Mathématiques",
                    "subject": "Algèbre",
                    "is_active": True
                },
                {
                    "user_id": "teacher2",
                    "employee_number": "EMP002",
                    "first_name": "Pierre",
                    "last_name": "Martin",
                    "email": "pierre.martin@presencepro.com",
                    "phone": "0123456790",
                    "department": "Sciences",
                    "subject": "Physique",
                    "is_active": True
                }
            ]
            
            for teacher_data in teachers_data:
                if not teacher_service.get_teacher_by_user_id(teacher_data["user_id"]):
                    teacher_create = TeacherCreate(**teacher_data)
                    teacher_service.create_teacher(teacher_create)
                    print(f"✅ Enseignant créé: {teacher_data['first_name']} {teacher_data['last_name']}")
                else:
                    print(f"⚠️  L'enseignant {teacher_data['user_id']} existe déjà")
            
            # Créer des étudiants
            students_data = [
                {
                    "user_id": "student1",
                    "student_number": "STU001",
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "email": "alice.johnson@student.presencepro.com",
                    "phone": "0123456791",
                    "class_name": "6ème A",
                    "academic_year": "2023-2024",
                    "is_active": True
                },
                {
                    "user_id": "student2",
                    "student_number": "STU002",
                    "first_name": "Bob",
                    "last_name": "Smith",
                    "email": "bob.smith@student.presencepro.com",
                    "phone": "0123456792",
                    "class_name": "6ème A",
                    "academic_year": "2023-2024",
                    "is_active": True
                },
                {
                    "user_id": "student3",
                    "student_number": "STU003",
                    "first_name": "Charlie",
                    "last_name": "Brown",
                    "email": "charlie.brown@student.presencepro.com",
                    "phone": "0123456793",
                    "class_name": "5ème B",
                    "academic_year": "2023-2024",
                    "is_active": True
                }
            ]
            
            for student_data in students_data:
                if not student_service.get_student_by_user_id(student_data["user_id"]):
                    student_create = StudentCreate(**student_data)
                    student_service.create_student(student_create)
                    print(f"✅ Étudiant créé: {student_data['first_name']} {student_data['last_name']}")
                else:
                    print(f"⚠️  L'étudiant {student_data['user_id']} existe déjà")
            
            # Créer des parents
            parents_data = [
                {
                    "user_id": "parent1",
                    "first_name": "Robert",
                    "last_name": "Johnson",
                    "email": "robert.johnson@parent.presencepro.com",
                    "phone": "0123456794",
                    "profession": "Ingénieur",
                    "emergency_contact": True,
                    "is_active": True
                },
                {
                    "user_id": "parent2",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "email": "sarah.johnson@parent.presencepro.com",
                    "phone": "0123456795",
                    "profession": "Médecin",
                    "emergency_contact": False,
                    "is_active": True
                },
                {
                    "user_id": "parent3",
                    "first_name": "Michael",
                    "last_name": "Smith",
                    "email": "michael.smith@parent.presencepro.com",
                    "phone": "0123456796",
                    "profession": "Professeur",
                    "emergency_contact": True,
                    "is_active": True
                }
            ]
            
            for parent_data in parents_data:
                if not parent_service.get_parent_by_user_id(parent_data["user_id"]):
                    parent_create = ParentCreate(**parent_data)
                    parent_service.create_parent(parent_create)
                    print(f"✅ Parent créé: {parent_data['first_name']} {parent_data['last_name']}")
                else:
                    print(f"⚠️  Le parent {parent_data['user_id']} existe déjà")
            
            # Créer des relations parent-élève
            print("🔗 Création des relations parent-élève...")
            
            # Récupérer les IDs
            alice = student_service.get_student_by_user_id("student1")
            bob = student_service.get_student_by_user_id("student2")
            robert = parent_service.get_parent_by_user_id("parent1")
            sarah = parent_service.get_parent_by_user_id("parent2")
            michael = parent_service.get_parent_by_user_id("parent3")
            
            relations = [
                # Alice Johnson - parents Robert et Sarah Johnson
                {"parent_id": robert.id, "student_id": alice.id, "relationship_type": "père", "is_primary_contact": True},
                {"parent_id": sarah.id, "student_id": alice.id, "relationship_type": "mère", "is_emergency_contact": True},
                # Bob Smith - parent Michael Smith
                {"parent_id": michael.id, "student_id": bob.id, "relationship_type": "père", "is_primary_contact": True, "is_emergency_contact": True}
            ]
            
            for relation_data in relations:
                if not parent_service.relation_exists(relation_data["parent_id"], relation_data["student_id"]):
                    relation_create = ParentStudentRelationCreate(**relation_data)
                    parent_service.create_parent_student_relation(relation_create)
                    print(f"✅ Relation créée: Parent {relation_data['parent_id']} - Élève {relation_data['student_id']}")
                else:
                    print(f"⚠️  La relation Parent {relation_data['parent_id']} - Élève {relation_data['student_id']} existe déjà")
            
            print()
            print("🎉 Initialisation terminée avec succès!")
            print()
            print("📝 Prochaines étapes:")
            print("   1. Lancez le service: uvicorn app.main:app --reload --port 8002")
            print("   2. Testez l'API: http://localhost:8002/docs")
            print("   3. Utilisez les tokens du service d'authentification")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False
    
    return True


if __name__ == "__main__":
    init_database()
