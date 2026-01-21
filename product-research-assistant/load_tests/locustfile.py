from locust import HttpUser, task, between
import json

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def query_product(self):
        payload = {"query": "What wireless headphones do we have in stock?"}
        self.client.post("/query", json=payload)

    @task(1)
    def query_search(self):
        payload = {"query": "Current market price for noise-cancelling headphones?"}
        self.client.post("/query", json=payload)

    @task(1)
    def query_analysis(self):
        payload = {"query": "Calculate margin for a product with price $100 and cost $60"}
        self.client.post("/query", json=payload)
    
    @task(1)
    def health_check(self):
        self.client.get("/health")
