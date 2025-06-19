"""
Tests pour les endpoints des cours
"""
import pytest
from fastapi.testclient import TestClient


class TestCourseEndpoints:
    """Tests pour les endpoints de gestion des cours"""
    
    def test_create_course_success(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de création d'un cours avec succès"""
        response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_course_data["name"]
        assert data["code"] == sample_course_data["code"]
        assert data["subject"] == sample_course_data["subject"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_course_duplicate_code(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de création d'un cours avec code dupliqué"""
        # Créer le premier cours
        client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Tenter de créer un cours avec le même code
        response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 400
        assert "existe déjà" in response.json()["detail"]
    
    def test_create_course_unauthorized(self, client: TestClient, mock_auth_student, sample_course_data):
        """Test de création d'un cours sans autorisation"""
        response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer student_token"}
        )
        
        assert response.status_code == 403
    
    def test_get_courses_list(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de récupération de la liste des cours"""
        # Créer quelques cours
        for i in range(3):
            course_data = sample_course_data.copy()
            course_data["code"] = f"TEST{i:03d}"
            course_data["name"] = f"Test Course {i}"
            client.post(
                "/courses/",
                json=course_data,
                headers={"Authorization": "Bearer admin_token"}
            )
        
        # Récupérer la liste
        response = client.get(
            "/courses/",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["courses"]) == 3
        assert data["total"] == 3
    
    def test_get_courses_with_filters(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de récupération des cours avec filtres"""
        # Créer des cours avec différentes matières
        subjects = ["Mathématiques", "Physique", "Français"]
        for i, subject in enumerate(subjects):
            course_data = sample_course_data.copy()
            course_data["code"] = f"TEST{i:03d}"
            course_data["subject"] = subject
            client.post(
                "/courses/",
                json=course_data,
                headers={"Authorization": "Bearer admin_token"}
            )
        
        # Filtrer par matière
        response = client.get(
            "/courses/?subject=Mathématiques",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["courses"]) == 1
        assert data["courses"][0]["subject"] == "Mathématiques"
    
    def test_get_course_by_id(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de récupération d'un cours par ID"""
        # Créer un cours
        create_response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        course_id = create_response.json()["id"]
        
        # Récupérer le cours
        response = client.get(
            f"/courses/{course_id}",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert data["name"] == sample_course_data["name"]
    
    def test_get_course_not_found(self, client: TestClient, mock_auth_service):
        """Test de récupération d'un cours inexistant"""
        response = client.get(
            "/courses/999",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 404
    
    def test_update_course(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de mise à jour d'un cours"""
        # Créer un cours
        create_response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        course_id = create_response.json()["id"]
        
        # Mettre à jour le cours
        update_data = {"name": "Updated Course Name", "credits": 5}
        response = client.put(
            f"/courses/{course_id}",
            json=update_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Course Name"
        assert data["credits"] == 5
        assert data["code"] == sample_course_data["code"]  # Inchangé
    
    def test_update_course_unauthorized(self, client: TestClient, mock_auth_student, sample_course_data):
        """Test de mise à jour d'un cours sans autorisation"""
        response = client.put(
            "/courses/1",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer student_token"}
        )
        
        assert response.status_code == 403
    
    def test_delete_course(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de suppression d'un cours"""
        # Créer un cours
        create_response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        course_id = create_response.json()["id"]
        
        # Supprimer le cours
        response = client.delete(
            f"/courses/{course_id}",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 204
        
        # Vérifier que le cours n'existe plus
        get_response = client.get(
            f"/courses/{course_id}",
            headers={"Authorization": "Bearer admin_token"}
        )
        assert get_response.status_code == 404
    
    def test_delete_course_unauthorized(self, client: TestClient, mock_auth_student):
        """Test de suppression d'un cours sans autorisation"""
        response = client.delete(
            "/courses/1",
            headers={"Authorization": "Bearer student_token"}
        )
        
        assert response.status_code == 403
    
    def test_search_courses(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de recherche de cours"""
        # Créer quelques cours
        courses_data = [
            {"name": "Advanced Mathematics", "code": "MATH001", "subject": "Mathematics"},
            {"name": "Basic Physics", "code": "PHYS001", "subject": "Physics"},
            {"name": "Mathematical Analysis", "code": "MATH002", "subject": "Mathematics"}
        ]
        
        for course_data in courses_data:
            full_data = sample_course_data.copy()
            full_data.update(course_data)
            client.post(
                "/courses/",
                json=full_data,
                headers={"Authorization": "Bearer admin_token"}
            )
        
        # Rechercher par terme
        response = client.get(
            "/courses/search?q=Math",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Advanced Mathematics et Mathematical Analysis
    
    def test_get_course_stats(self, client: TestClient, mock_auth_service, sample_course_data):
        """Test de récupération des statistiques d'un cours"""
        # Créer un cours
        create_response = client.post(
            "/courses/",
            json=sample_course_data,
            headers={"Authorization": "Bearer admin_token"}
        )
        course_id = create_response.json()["id"]
        
        # Récupérer les statistiques
        response = client.get(
            f"/courses/{course_id}/stats",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "course_id" in data
        assert "total_students" in data
        assert "total_teachers" in data
        assert "total_schedules" in data
        assert data["course_id"] == course_id
