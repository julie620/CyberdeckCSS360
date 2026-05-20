# CI/CD Pipeline User Guide — CyberdeckCSS360

This guide explains how to use the existing CI/CD pipeline. It assumes the pipeline is already set up in the repository.

---

## How It Works

Every time code is pushed to `main`, GitHub automatically runs the pipeline. It goes through 5 stages in order:

1. **Static Analysis** — checks code style and catches common errors
2. **Tests** — runs unit, integration, and smoke tests
3. **Build** — packages the app into a Docker image
4. **Deploy** — sends the new version to the Raspberry Pi
5. **Verify** — confirms the live app is responding

If any stage fails, everything after it is skipped automatically.

---

## Triggering the Pipeline

The pipeline runs automatically on two events:

- **Push to `main`** — runs all 5 stages including deploy
- **Pull request to `main`** — runs lint and tests only (does not deploy)

You do not need to manually start it. Just push your code:

```bash
git add .
git commit -m "your message"
git push origin main
```

---

## Watching It Run

1. Go to the repository on GitHub
2. Click the **Actions** tab at the top
3. Click the most recent workflow run in the list
4. Click any stage to expand its live logs

A green checkmark means it passed. A red X means it failed.

---

## If a Stage Fails

**Static Analysis fails**
- Run `npm run lint` locally and fix any errors it reports
- Run `pylint api/ --ignore=venv` locally for Python errors
- Commit the fixes and push again

**Tests fail**
- Run `pytest api/tests/` locally to see which test failed and why
- Fix the code or the test, then push again

**Build fails**
- Usually means the Dockerfile has an error or a dependency is missing
- Try `docker build -t test .` locally to debug

**Deploy fails**
- The Raspberry Pi may be off or unreachable
- Check that the Pi is powered on and connected to the network
- Confirm its IP address hasn't changed (`hostname -I` on the Pi)

**Verify fails**
- The app may need more time to start up after deploying
- Check the Pi directly: `ssh pi@<pi-ip>` then `docker ps` to see if the container is running

---

## Checking the Live App

Once the pipeline finishes successfully, the app is live at:

- **Frontend:** `http://<pi-ip>:5173`
- **API:** `http://<pi-ip>:5000`

You need to be on the same network as the Raspberry Pi to access these.

---

## Pulling the Latest Code Locally

To make sure you're working with the latest version before making changes:

```bash
git pull origin main
```

Always do this before starting new work to avoid merge conflicts.
