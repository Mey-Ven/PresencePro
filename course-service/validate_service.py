"""
Script de validation complète du service de cours PresencePro
"""
import asyncio
import httpx
import json
from datetime import date, time


async def test_course_api():
    """Test complet de l'API des cours"""
    base_url = "http://localhost:8003"
    
    print("🧪 Test complet de l'API Course Service")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Test de santé
            print("1. Test de santé...")
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200
            print("✅ Service en bonne santé")
            
            # 2. Test création de cours
            print("\n2. Test création de cours...")
            import random
            random_code = f"API{random.randint(100, 999)}"
            course_data = {
                "name": "Test Course API",
                "code": random_code,
                "description": "Cours de test pour l'API",
                "subject": "Test",
                "level": "6ème",
                "credits": 3,
                "max_students": 25,
                "academic_year": "2023-2024",
                "semester": "Semestre 1"
            }
            
            response = await client.post(f"{base_url}/courses/", json=course_data)
            assert response.status_code == 201
            course = response.json()
            course_id = course["id"]
            print(f"✅ Cours créé avec ID: {course_id}")
            
            # 3. Test récupération de cours
            print("\n3. Test récupération de cours...")
            response = await client.get(f"{base_url}/courses/{course_id}")
            assert response.status_code == 200
            retrieved_course = response.json()
            assert retrieved_course["name"] == course_data["name"]
            print("✅ Cours récupéré avec succès")
            
            # 4. Test liste des cours
            print("\n4. Test liste des cours...")
            response = await client.get(f"{base_url}/courses/")
            assert response.status_code == 200
            courses_list = response.json()
            assert "courses" in courses_list
            assert len(courses_list["courses"]) >= 1
            print(f"✅ Liste récupérée: {courses_list['total']} cours")
            
            # 5. Test recherche de cours
            print("\n5. Test recherche de cours...")
            response = await client.get(f"{base_url}/courses/search?q=Test")
            assert response.status_code == 200
            search_results = response.json()
            assert len(search_results) >= 1
            print(f"✅ Recherche réussie: {len(search_results)} résultats")
            
            # 6. Test création d'emploi du temps
            print("\n6. Test création d'emploi du temps...")
            schedule_data = {
                "course_id": course_id,
                "day_of_week": "friday",
                "start_time": "14:00:00",
                "end_time": "15:30:00",
                "room": "TEST101",
                "building": "Bâtiment Test",
                "start_date": "2023-09-01",
                "end_date": "2024-01-31"
            }
            
            response = await client.post(f"{base_url}/schedules/", json=schedule_data)
            assert response.status_code == 201
            schedule = response.json()
            schedule_id = schedule["id"]
            print(f"✅ Emploi du temps créé avec ID: {schedule_id}")
            
            # 7. Test emploi du temps hebdomadaire
            print("\n7. Test emploi du temps hebdomadaire...")
            response = await client.get(f"{base_url}/schedules/weekly")
            assert response.status_code == 200
            weekly_schedule = response.json()
            assert "monday" in weekly_schedule
            print("✅ Emploi du temps hebdomadaire récupéré")
            
            # 8. Test création d'attribution
            print("\n8. Test création d'attribution...")
            assignment_data = {
                "course_id": course_id,
                "user_id": "teacher1",
                "assignment_type": "teacher",
                "is_primary": True,
                "valid_from": "2023-09-01",
                "valid_to": "2024-06-30"
            }
            
            response = await client.post(f"{base_url}/assignments/", json=assignment_data)
            assert response.status_code == 201
            assignment = response.json()
            assignment_id = assignment["id"]
            print(f"✅ Attribution créée avec ID: {assignment_id}")
            
            # 9. Test statistiques de cours
            print("\n9. Test statistiques de cours...")
            response = await client.get(f"{base_url}/courses/{course_id}/stats")
            assert response.status_code == 200
            stats = response.json()
            assert "total_students" in stats
            assert "total_teachers" in stats
            print("✅ Statistiques récupérées")
            
            # 10. Test mise à jour de cours
            print("\n10. Test mise à jour de cours...")
            update_data = {"name": "Test Course API Updated", "credits": 4}
            response = await client.put(f"{base_url}/courses/{course_id}", json=update_data)
            assert response.status_code == 200
            updated_course = response.json()
            assert updated_course["name"] == "Test Course API Updated"
            assert updated_course["credits"] == 4
            print("✅ Cours mis à jour avec succès")
            
            print("\n🎉 Tous les tests API ont réussi !")
            return True
            
        except AssertionError as e:
            print(f"❌ Test échoué: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return False


def test_data_integrity():
    """Test de l'intégrité des données"""
    print("\n📊 Test d'intégrité des données")
    print("-" * 30)
    
    # Vérifier que la base de données existe
    import os
    if os.path.exists("presencepro_courses.db"):
        print("✅ Base de données SQLite trouvée")
    else:
        print("❌ Base de données SQLite manquante")
        return False
    
    # Vérifier les modèles
    try:
        from app.models.course import Course, Schedule, CourseAssignment
        print("✅ Modèles importés avec succès")
    except ImportError as e:
        print(f"❌ Erreur d'import des modèles: {e}")
        return False
    
    # Vérifier les services
    try:
        from app.services.course_service import CourseService
        from app.services.schedule_service import ScheduleService
        from app.services.assignment_service import AssignmentService
        print("✅ Services importés avec succès")
    except ImportError as e:
        print(f"❌ Erreur d'import des services: {e}")
        return False
    
    return True


def test_configuration():
    """Test de la configuration"""
    print("\n⚙️ Test de configuration")
    print("-" * 30)
    
    try:
        from app.core.config import settings
        print(f"✅ Service: {settings.service_name}")
        print(f"✅ Version: {settings.service_version}")
        print(f"✅ Port: {settings.service_port}")
        print(f"✅ Base de données: {settings.database_url}")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False


async def main():
    """Fonction principale de validation"""
    print("🚀 Validation complète du Course Service PresencePro")
    print("=" * 60)
    
    # Tests de configuration
    config_ok = test_configuration()
    
    # Tests d'intégrité
    integrity_ok = test_data_integrity()
    
    # Tests API
    api_ok = await test_course_api()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DE LA VALIDATION")
    print("=" * 60)
    
    print(f"Configuration:     {'✅ OK' if config_ok else '❌ ERREUR'}")
    print(f"Intégrité données: {'✅ OK' if integrity_ok else '❌ ERREUR'}")
    print(f"Tests API:         {'✅ OK' if api_ok else '❌ ERREUR'}")
    
    all_ok = config_ok and integrity_ok and api_ok
    
    if all_ok:
        print("\n🎉 VALIDATION RÉUSSIE !")
        print("Le service Course Service est entièrement fonctionnel.")
        print("\n📝 Prochaines étapes:")
        print("   1. Intégrer l'authentification avec auth-service")
        print("   2. Tester l'intégration avec user-service")
        print("   3. Déployer en production avec PostgreSQL")
    else:
        print("\n❌ VALIDATION ÉCHOUÉE")
        print("Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return all_ok


if __name__ == "__main__":
    asyncio.run(main())
