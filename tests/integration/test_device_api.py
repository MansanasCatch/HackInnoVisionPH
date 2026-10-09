"""Integration tests for Device & AI Model setup API endpoints."""

from fastapi.testclient import TestClient


def test_device_specs_workflow(client: TestClient) -> None:
    # 1. Create onboarding account first
    ob_res = client.post(
        "/api/v1/onboarding",
        json={"username": "Tech User", "interests": ["AI", "Physics"], "age": 25},
    )
    assert ob_res.status_code == 201
    onboarding_id = ob_res.json()["id"]

    # 2. Auto-detect hardware specs
    detect_res = client.get("/api/v1/device/suggestions")
    assert detect_res.status_code == 200
    suggestions = detect_res.json()
    assert "models" in suggestions
    assert len(suggestions["models"]) >= 5
    assert any("reason" in m for m in suggestions["models"])

    # 3. Setup device specs for account
    device_payload = {
        "onboarding_id": onboarding_id,
        "ram_gb": 16.0,
        "gpu_name": "NVIDIA GeForce RTX 3060",
        "vram_gb": 6.0,
        "cpu_cores": 8,
        "storage_free_gb": 120.0,
        "os_name": "Windows 11",
        "selected_model": "llama3.2:3b",
    }
    setup_res = client.post("/api/v1/device", json=device_payload)
    assert setup_res.status_code == 201
    device_data = setup_res.json()
    assert device_data["onboarding_id"] == onboarding_id
    assert device_data["selected_model"] == "llama3.2:3b"

    # 4. Fetch device specs for account
    get_res = client.get(f"/api/v1/device/account/{onboarding_id}")
    assert get_res.status_code == 200
    assert get_res.json()["ram_gb"] == 16.0

    # 5. Runtime switch active local model
    switch_res = client.post(
        "/api/v1/device/select-model",
        json={
            "onboarding_id": onboarding_id,
            "selected_model": "gemma2:2b",
            "auto_pull": False,
        },
    )
    assert switch_res.status_code == 200
    assert switch_res.json()["selected_model"] == "gemma2:2b"

    # 6. Verify active model endpoint for AI
    active_res = client.get(f"/api/v1/device/active-model?onboarding_id={onboarding_id}")
    assert active_res.status_code == 200
    assert active_res.json()["active_model"] == "gemma2:2b"

    # 7. Check local Ollama endpoint
    ollama_res = client.get("/api/v1/device/ollama/models")
    assert ollama_res.status_code == 200
    assert "installed_models" in ollama_res.json()
