from locust import HttpUser, task, between
import random

class URLShortenerUser(HttpUser):
    wait_time = between(1, 2)
    short_ids = []

    @task(2)
    def shorten_url(self):
        """Create a short URL"""
        payload = {
            "long_url": f"https://example.com/page-{random.randint(1000, 9999)}",
            "user_id": 1
        }
        with self.client.post("/api/shorten", json=payload, catch_response=True) as res:
            if res.status_code == 200:
                try:
                    short_id = res.json()["short_url"].split("/")[-1]
                    self.short_ids.append(short_id)
                except Exception:
                    res.failure("Invalid JSON structure")
            else:
                res.failure(f"Shorten failed ({res.status_code})")

    @task(3)
    def redirect(self):
        """Redirect to long URL"""
        if not self.short_ids:
            return
        short_id = random.choice(self.short_ids)
        with self.client.get(f"/{short_id}", allow_redirects=False, catch_response=True) as res:
            if res.status_code not in [301, 302]:
                res.failure(f"Redirect failed for {short_id}")

    @task(1)
    def recent_urls(self):
        """Fetch recent URLs"""
        with self.client.get("/api/urls/recent", catch_response=True) as res:
            if res.status_code != 200:
                res.failure("Failed to fetch recent URLs")

    @task(1)
    def delete_url(self):
        """Delete a random URL"""
        if not self.short_ids:
            return
        short_id = random.choice(self.short_ids)
        with self.client.delete(f"/api/urls/{short_id}", catch_response=True) as res:
            if res.status_code == 200:
                self.short_ids.remove(short_id)
