# Chadwick Lundgren: Portfolio

Static portfolio site (plain HTML, CSS and a few lines of JavaScript). No build step.

## Put it online with GitHub Pages

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
