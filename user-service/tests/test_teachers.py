"""
Tests pour les endpoints des enseignants
"""
import pytest
from fastapi import status


class TestTeacherEndpoints:
    """Tests pour les endpoints des enseignants"""
    
    def test_create_teacher_success(self, client, mock_auth_service, sample_teacher_data):
        """Test de création d'un enseignant avec succès"""
        response = client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == sample_teacher_data["user_id"]
        assert data["employee_number"] == sample_teacher_data["employee_number"]
        assert data["first_name"] == sample_teacher_data["first_name"]
        assert data["last_name"] == sample_teacher_data["last_name"]
        assert data["email"] == sample_teacher_data["email"]
        assert data["department"] == sample_teacher_data["department"]
    
    def test_create_teacher_duplicate_user_id(self, client, mock_auth_service, sample_teacher_data):
        """Test de création d'un enseignant avec user_id dupliqué"""
        # Créer le premier enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Essayer de créer un deuxième enseignant avec le même user_id
        response = client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "user_id existe déjà" in response.json()["detail"]
    
    def test_create_teacher_duplicate_employee_number(self, client, mock_auth_service, sample_teacher_data):
        """Test de création d'un enseignant avec numéro d'employé dupliqué"""
        # Créer le premier enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Modifier le user_id mais garder le même numéro d'employé
        duplicate_data = sample_teacher_data.copy()
        duplicate_data["user_id"] = "different_user_id"
        
        response = client.post(
            "/teachers/",
            json=duplicate_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "numéro d'employé existe déjà" in response.json()["detail"]
    
    def test_get_teachers_success(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de récupération de la liste des enseignants"""
        # Créer un enseignant d'abord
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer la liste
        response = client.get(
            "/teachers/",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == sample_teacher_data["user_id"]
    
    def test_get_teachers_with_department_filter(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de récupération avec filtre par département"""
        # Créer un enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer avec filtre
        response = client.get(
            f"/teachers/?department={sample_teacher_data['department']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["department"] == sample_teacher_data["department"]
    
    def test_search_teachers(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de recherche d'enseignants"""
        # Créer un enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Rechercher par nom
        response = client.get(
            f"/teachers/search?q={sample_teacher_data['first_name']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_teachers_by_department(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de récupération des enseignants par département"""
        # Créer un enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer par département
        response = client.get(
            f"/teachers/by-department/{sample_teacher_data['department']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_teachers_by_subject(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de récupération des enseignants par matière"""
        # Créer un enseignant
        client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer par matière
        response = client.get(
            f"/teachers/by-subject/{sample_teacher_data['subject']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_teacher_by_id(self, client, mock_auth_teacher, sample_teacher_data):
        """Test de récupération d'un enseignant par ID"""
        # Créer un enseignant
        create_response = client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        teacher_id = create_response.json()["id"]
        
        # Récupérer par ID
        response = client.get(
            f"/teachers/{teacher_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == teacher_id
        assert data["user_id"] == sample_teacher_data["user_id"]
    
    def test_update_teacher_success(self, client, mock_auth_service, sample_teacher_data):
        """Test de mise à jour d'un enseignant"""
        # Créer un enseignant
        create_response = client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        teacher_id = create_response.json()["id"]
        
        # Mettre à jour
        update_data = {"department": "Updated Department"}
        response = client.put(
            f"/teachers/{teacher_id}",
            json=update_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["department"] == "Updated Department"
        assert data["subject"] == sample_teacher_data["subject"]  # Inchangé
    
    def test_delete_teacher_success(self, client, mock_auth_service, sample_teacher_data):
        """Test de suppression d'un enseignant"""
        # Créer un enseignant
        create_response = client.post(
            "/teachers/",
            json=sample_teacher_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        teacher_id = create_response.json()["id"]
        
        # Supprimer
        response = client.delete(
            f"/teachers/{teacher_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_unauthorized_access(self, client, sample_teacher_data):
        """Test d'accès non autorisé"""
        response = client.post(
            "/teachers/",
            json=sample_teacher_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
