"""
Tests pour les endpoints des parents et relations parent-élève
"""
import pytest
from fastapi import status


class TestParentEndpoints:
    """Tests pour les endpoints des parents"""
    
    def test_create_parent_success(self, client, mock_auth_service, sample_parent_data):
        """Test de création d'un parent avec succès"""
        response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == sample_parent_data["user_id"]
        assert data["first_name"] == sample_parent_data["first_name"]
        assert data["last_name"] == sample_parent_data["last_name"]
        assert data["email"] == sample_parent_data["email"]
        assert data["profession"] == sample_parent_data["profession"]
    
    def test_create_parent_duplicate_user_id(self, client, mock_auth_service, sample_parent_data):
        """Test de création d'un parent avec user_id dupliqué"""
        # Créer le premier parent
        client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Essayer de créer un deuxième parent avec le même user_id
        response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "user_id existe déjà" in response.json()["detail"]
    
    def test_get_parents_success(self, client, mock_auth_teacher, sample_parent_data):
        """Test de récupération de la liste des parents"""
        # Créer un parent d'abord
        client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer la liste
        response = client.get(
            "/parents/",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == sample_parent_data["user_id"]
    
    def test_search_parents(self, client, mock_auth_teacher, sample_parent_data):
        """Test de recherche de parents"""
        # Créer un parent
        client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Rechercher par nom
        response = client.get(
            f"/parents/search?q={sample_parent_data['first_name']}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_parent_by_id(self, client, mock_auth_teacher, sample_parent_data):
        """Test de récupération d'un parent par ID"""
        # Créer un parent
        create_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = create_response.json()["id"]
        
        # Récupérer par ID
        response = client.get(
            f"/parents/{parent_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == parent_id
        assert data["user_id"] == sample_parent_data["user_id"]
    
    def test_update_parent_success(self, client, mock_auth_service, sample_parent_data):
        """Test de mise à jour d'un parent"""
        # Créer un parent
        create_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = create_response.json()["id"]
        
        # Mettre à jour
        update_data = {"profession": "Updated Profession"}
        response = client.put(
            f"/parents/{parent_id}",
            json=update_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["profession"] == "Updated Profession"
        assert data["first_name"] == sample_parent_data["first_name"]  # Inchangé
    
    def test_delete_parent_success(self, client, mock_auth_service, sample_parent_data):
        """Test de suppression d'un parent"""
        # Créer un parent
        create_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = create_response.json()["id"]
        
        # Supprimer
        response = client.delete(
            f"/parents/{parent_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestParentStudentRelations:
    """Tests pour les relations parent-élève"""
    
    def test_create_parent_student_relation_success(self, client, mock_auth_service, sample_parent_data, sample_student_data):
        """Test de création d'une relation parent-élève"""
        # Créer un parent
        parent_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = parent_response.json()["id"]
        
        # Créer un étudiant
        student_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = student_response.json()["id"]
        
        # Créer la relation
        response = client.post(
            f"/parents/{parent_id}/students/{student_id}?relationship_type=père&is_primary_contact=true",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["parent_id"] == parent_id
        assert data["student_id"] == student_id
        assert data["relationship_type"] == "père"
        assert data["is_primary_contact"] == True
    
    def test_create_duplicate_relation(self, client, mock_auth_service, sample_parent_data, sample_student_data):
        """Test de création d'une relation dupliquée"""
        # Créer un parent et un étudiant
        parent_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = parent_response.json()["id"]
        
        student_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = student_response.json()["id"]
        
        # Créer la première relation
        client.post(
            f"/parents/{parent_id}/students/{student_id}?relationship_type=père",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Essayer de créer une relation dupliquée
        response = client.post(
            f"/parents/{parent_id}/students/{student_id}?relationship_type=mère",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "existe déjà" in response.json()["detail"]
    
    def test_get_parent_students(self, client, mock_auth_teacher, sample_parent_data, sample_student_data):
        """Test de récupération des étudiants d'un parent"""
        # Créer un parent et un étudiant
        parent_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = parent_response.json()["id"]
        
        student_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = student_response.json()["id"]
        
        # Créer la relation
        client.post(
            f"/parents/{parent_id}/students/{student_id}?relationship_type=père",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Récupérer les étudiants du parent
        response = client.get(
            f"/parents/{parent_id}/students",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == student_id
    
    def test_delete_parent_student_relation(self, client, mock_auth_service, sample_parent_data, sample_student_data):
        """Test de suppression d'une relation parent-élève"""
        # Créer un parent et un étudiant
        parent_response = client.post(
            "/parents/",
            json=sample_parent_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        parent_id = parent_response.json()["id"]
        
        student_response = client.post(
            "/students/",
            json=sample_student_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        student_id = student_response.json()["id"]
        
        # Créer la relation
        relation_response = client.post(
            f"/parents/{parent_id}/students/{student_id}?relationship_type=père",
            headers={"Authorization": "Bearer fake-token"}
        )
        relation_id = relation_response.json()["id"]
        
        # Supprimer la relation
        response = client.delete(
            f"/parents/relations/{relation_id}",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_unauthorized_access(self, client, sample_parent_data):
        """Test d'accès non autorisé"""
        response = client.post(
            "/parents/",
            json=sample_parent_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
