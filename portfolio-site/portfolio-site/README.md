# Chadwick Lundgren: Portfolio

Static portfolio site (plain HTML, CSS and a few lines of JavaScript). No build step.

## Put it online with GitHub Pages (this repo)

This repo already includes `.github/workflows/pages.yml`, which publishes this folder.

1. Merge into `main`.
2. In the repo go to Settings, then Pages. Under "Build and deployment" set Source to **GitHub Actions**.
3. The workflow runs on every push to `main` (or run it by hand from the Actions tab).
   The site goes live at `https://grandypurpp.github.io/Portfolio/`.

## Client project manager

The "Start a project" section (`#start`) lets a client pick services, fill in their details and get a
project board: tasks grouped by phase (Discovery, Audit and plan, Build, Launch, Support and improve),
who owns each task, a rough timeline and a progress bar. The board is saved in the client's browser
(localStorage) and can be emailed to you or copied. To change the services or tasks, edit the
`SERVICES` and `PHASES` lists in the script at the bottom of `index.html`.

## Put it online with GitHub Pages (new repo)

1. On github.com, create a new public repository, for example `portfolio`.
2. Upload everything in this folder: `index.html`, the `images` folder, `.nojekyll`, and this README.
   (On the new repo page choose "uploading an existing file" and drag the files in.)
3. In the repo go to Settings, then Pages. Under "Build and deployment" choose
   "Deploy from a branch", pick the `main` branch and the `/ (root)` folder, then Save.
4. After a minute or two the site is live at `https://YOUR-USERNAME.github.io/portfolio/`.
   Put that link on your applications.

## Using git instead

```bash
cd portfolio-site
git init
git add .
git commit -m "Add portfolio site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/portfolio.git
git push -u origin main
```

## Updating later

Edit `index.html` (or replace files in `images/`) and commit again. GitHub Pages republishes automatically.
