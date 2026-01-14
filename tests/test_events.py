import pytest


class TestEventEndpoints:
    """
    Tests para los endpoints de eventos.
    """

    def test_read_root(self, client):
        """
        Test del endpoint raíz.
        """
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Tech Events API"
        assert "version" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """
        Test del health check endpoint.
        """
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_create_event_success(self, client, sample_event):
        """
        Test crear evento exitosamente.
        """
        response = client.post("/api/v1/events", json=sample_event)
        assert response.status_code == 201
        data = response.json()

        assert "_id" in data
        assert data["title"] == sample_event["title"]
        assert data["description"] == sample_event["description"]
        assert data["location"] == sample_event["location"]
        assert data["organizer"] == sample_event["organizer"]
        assert data["capacity"] == sample_event["capacity"]
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_event_past_date(self, client, sample_event):
        """
        Test crear evento con fecha en el pasado (debe fallar).
        """
        past_event = sample_event.copy()
        past_event["date"] = "2020-01-01T10:00:00"

        response = client.post("/api/v1/events", json=past_event)
        assert response.status_code == 422  # Validation error

    def test_create_event_invalid_email(self, client, sample_event):
        """
        Test crear evento con email inválido (debe fallar).
        """
        invalid_event = sample_event.copy()
        invalid_event["organizer"] = "not-an-email"

        response = client.post("/api/v1/events", json=invalid_event)
        assert response.status_code == 422  # Validation error

    def test_create_event_negative_capacity(self, client, sample_event):
        """
        Test crear evento con capacidad negativa (debe fallar).
        """
        invalid_event = sample_event.copy()
        invalid_event["capacity"] = -10

        response = client.post("/api/v1/events", json=invalid_event)
        assert response.status_code == 422  # Validation error

    def test_get_events_list(self, client):
        """
        Test obtener lista de eventos.
        """
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_get_events_with_pagination(self, client):
        """
        Test paginación de eventos.
        """
        response = client.get("/api/v1/events?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["events"]) <= 5

    def test_get_events_with_tags_filter(self, client):
        """
        Test filtrado por tags.
        """
        response = client.get("/api/v1/events?tags=python,test")
        assert response.status_code == 200
        data = response.json()

        assert "events" in data

    def test_get_event_by_id_invalid(self, client):
        """
        Test obtener evento con ID inválido.
        """
        response = client.get("/api/v1/events/invalid-id")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_get_event_by_id_not_found(self, client):
        """
        Test obtener evento que no existe.
        """
        fake_id = "507f1f77bcf86cd799439011"  # ObjectId válido pero no existe
        response = client.get(f"/api/v1/events/{fake_id}")
        assert response.status_code == 404

    def test_update_event_not_found(self, client):
        """
        Test actualizar evento que no existe.
        """
        fake_id = "507f1f77bcf86cd799439011"
        update_data = {"title": "Updated Title"}

        response = client.put(f"/api/v1/events/{fake_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_event_not_found(self, client):
        """
        Test eliminar evento que no existe.
        """
        fake_id = "507f1f77bcf86cd799439011"
        response = client.delete(f"/api/v1/events/{fake_id}")
        assert response.status_code == 404


class TestEventWorkflow:
    """
    Test del flujo completo: crear, obtener, actualizar, eliminar.
    """

    @pytest.fixture(autouse=True)
    def setup(self, client, sample_event):
        """
        Setup para cada test: crear un evento.
        """
        self.client = client
        self.sample_event = sample_event

        # Crear evento
        response = self.client.post("/api/v1/events", json=self.sample_event)
        self.event_id = response.json()["_id"]

    def test_full_crud_workflow(self):
        """
        Test del flujo completo CRUD.
        """
        # 1. Obtener el evento creado
        response = self.client.get(f"/api/v1/events/{self.event_id}")
        assert response.status_code == 200
        event = response.json()
        assert event["title"] == self.sample_event["title"]

        # 2. Actualizar el evento
        update_data = {"title": "Updated Conference 2025"}
        response = self.client.put(f"/api/v1/events/{self.event_id}", json=update_data)
        assert response.status_code == 200
        updated_event = response.json()
        assert updated_event["title"] == "Updated Conference 2025"

        # 3. Verificar que aparece en la lista
        response = self.client.get("/api/v1/events")
        assert response.status_code == 200
        events_list = response.json()["events"]
        event_ids = [e["_id"] for e in events_list]
        assert self.event_id in event_ids

        # 4. Eliminar el evento
        response = self.client.delete(f"/api/v1/events/{self.event_id}")
        assert response.status_code == 204

        # 5. Verificar que ya no existe
        response = self.client.get(f"/api/v1/events/{self.event_id}")
        assert response.status_code == 404
