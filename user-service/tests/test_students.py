"""
Tests pour les endpoints des étudiants
"""
import pytest
from fastapi import status


class TestStudentEndpoints:
    """Tests pour les endpoints des étudiants"""
    
    def test_create_student_success(self, client, mock_auth_service, sample_student_data):
        """Test de création d'un étudiant avec succès"""
        response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == sample_student_data["user_id"]
        assert data["student_number"] == sample_student_data["student_number"]
        assert data["first_name"] == sample_student_data["first_name"]
        assert data["last_name"] == sample_student_data["last_name"]
        assert data["email"] == sample_student_data["email"]
    
    def test_create_student_duplicate_user_id(self, client, mock_auth_service, sample_student_data):
        """Test de création d'un étudiant avec user_id dupliqué"""
        # Créer le premier étudiant
        client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Essayer de créer un deuxième étudiant avec le même user_id
        response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "user_id existe déjà" in response.json()["detail"]
    
    def test_create_student_duplicate_student_number(self, client, mock_auth_service, sample_student_data):
        """Test de création d'un étudiant avec numéro dupliqué"""
        # Créer le premier étudiant
        client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Modifier le user_id mais garder le même numéro d'étudiant
        duplicate_data = sample_student_data.copy()
        duplicate_data["user_id"] = "different_user_id"
        
        response = client.post(
            "/students/",
            json=duplicate_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "numéro existe déjà" in response.json()["detail"]
    
    def test_get_students_success(self, client, mock_auth_teacher, sample_student_data):
        """Test de récupération de la liste des étudiants"""
        # Créer un étudiant d'abord
        client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer la liste
        response = client.get(
            "/students/",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == sample_student_data["user_id"]
    
    def test_get_students_with_pagination(self, client, mock_auth_teacher):
        """Test de récupération avec pagination"""
        response = client.get(
            "/students/?skip=0&limit=10",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_students_with_class_filter(self, client, mock_auth_teacher, sample_student_data):
        """Test de récupération avec filtre par classe"""
        # Créer un étudiant
        client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer avec filtre
        response = client.get(
            f"/students/?class_name={sample_student_data['class_name']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["class_name"] == sample_student_data["class_name"]
    
    def test_search_students(self, client, mock_auth_teacher, sample_student_data):
        """Test de recherche d'étudiants"""
        # Créer un étudiant
        client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Rechercher par nom
        response = client.get(
            f"/students/search?q={sample_student_data['first_name']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_student_by_id(self, client, mock_auth_teacher, sample_student_data):
        """Test de récupération d'un étudiant par ID"""
        # Créer un étudiant
        create_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = create_response.json()["id"]
        
        # Récupérer par ID
        response = client.get(
            f"/students/{student_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == student_id
        assert data["user_id"] == sample_student_data["user_id"]
    
    def test_get_student_not_found(self, client, mock_auth_teacher):
        """Test de récupération d'un étudiant inexistant"""
        response = client.get(
            "/students/999",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "non trouvé" in response.json()["detail"]
    
    def test_update_student_success(self, client, mock_auth_service, sample_student_data):
        """Test de mise à jour d'un étudiant"""
        # Créer un étudiant
        create_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = create_response.json()["id"]
        
        # Mettre à jour
        update_data = {"first_name": "Updated Name"}
        response = client.put(
            f"/students/{student_id}",
            json=update_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated Name"
        assert data["last_name"] == sample_student_data["last_name"]  # Inchangé
    
    def test_update_student_not_found(self, client, mock_auth_service):
        """Test de mise à jour d'un étudiant inexistant"""
        update_data = {"first_name": "Updated Name"}
        response = client.put(
            "/students/999",
            json=update_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "non trouvé" in response.json()["detail"]
    
    def test_delete_student_success(self, client, mock_auth_service, sample_student_data):
        """Test de suppression d'un étudiant"""
        # Créer un étudiant
        create_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = create_response.json()["id"]
        
        # Supprimer
        response = client.delete(
            f"/students/{student_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_student_not_found(self, client, mock_auth_service):
        """Test de suppression d'un étudiant inexistant"""
        response = client.delete(
            "/students/999",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "non trouvé" in response.json()["detail"]
    
    def test_unauthorized_access(self, client, sample_student_data):
        """Test d'accès non autorisé"""
        response = client.post(
            "/students/",
            json=sample_student_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
