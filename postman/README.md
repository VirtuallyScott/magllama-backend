# magllama Postman Collection

This directory contains a Postman collection and environment for testing the magllama API.

## Usage

1. Import `magllama-api.postman_collection.json` into Postman.
2. Import `magllama-api.postman_environment.json` as an environment.
3. Set your `username`, `password`, and `user_id` in the environment.
4. Run the `Authenticate (Login)` request to obtain an authentication token.
5. All subsequent requests will use the `auth_token` variable for authentication.

## Notes

- The collection assumes the API returns a token on login. If your API uses API keys or a different auth mechanism, adjust the collection accordingly.
- Add or modify requests in the collection as your API evolves.
- The `base_url` variable allows you to easily switch between environments (local, staging, production).
