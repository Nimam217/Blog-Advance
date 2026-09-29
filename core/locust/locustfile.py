from locust import HttpUser, task


class QuickstartUser(HttpUser):

    def on_start(self):
        response = self.client.post(
            "/accounts/api/v1/jwt/token/",
            json={"email": "admin@gmail.com", "password": "123"},
        )

        data = response.json()

        self.headers = {"Authorization": f"Bearer {data['access']}"}

    @task
    def post_list(self):
        self.client.get("/blog/api/v1/post/", headers=self.headers)
