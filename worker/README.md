## Demucs worker (experimental)

This is intentionally isolated on branch `feature/demucs-worker`, not deployed to the live Render service. Requires a separate host with adequate RAM, preferably GPU. Protect the endpoint with `ACA_WORKER_TOKEN` (required); send `Authorization: Bearer <token>` with a multipart audio file to `POST /separate`.

Returns ZIP containing bass.wav, drums.wav, vocals.wav, other.wav. Never expose token in browser JS. The eventual main backend should call this worker server-to-server. No model runtime tests yet; test memory, output quality and authorization before production. If called on demand the first run may download model weights.
