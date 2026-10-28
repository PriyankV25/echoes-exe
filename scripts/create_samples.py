"""
Echoes.exe — Script & Module to create verifiable sample repositories.
"""
import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "samples"


def create_sample_canvas_nest():
    s1 = SAMPLES_DIR / "canvas-nest-legacy"
    s1.mkdir(parents=True, exist_ok=True)

    (s1 / "package.json").write_text('''{
  "name": "canvas-nest-legacy",
  "version": "1.0.4",
  "description": "An unmaintained particle canvas background visualizer for the ghost terminal era.",
  "main": "src/canvas-nest.js",
  "scripts": {
    "build": "webpack --mode production",
    "test": "mocha tests/"
  },
  "author": "Ghost Developer (ghost@void.net)",
  "license": "MIT",
  "dependencies": {
    "webpack": "^3.10.0",
    "babel-core": "^6.26.0",
    "request": "^2.88.2"
  },
  "devDependencies": {
    "mocha": "^5.2.0"
  }
}''', encoding="utf-8")

    (s1 / "README.md").write_text('''# canvas-nest-legacy

> An interactive particle nest background library written in vanilla JavaScript.

## Features
- Lightweight canvas rendering
- Particle proximity calculations
- Zero runtime dependencies (originally)

## Last Observed State
Last updated in late 2017. Unmaintained after maintainers shifted to WebGL shaders.
''', encoding="utf-8")

    (s1 / "LICENSE").write_text('''MIT License

Copyright (c) 2016-2017 Spectral Maintainers

Permission is hereby granted, free of charge, to any person obtaining a copy of this software.
''', encoding="utf-8")

    src_dir = s1 / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "canvas-nest.js").write_text('''/**
 * Canvas Nest Legacy Visualizer
 * Last maintained in 2017.
 */
function CanvasNest(element, config) {
    this.element = element;
    this.config = config || {};
    this.points = [];
}

CanvasNest.prototype.init = function() {
    console.log('[canvas-nest] Initializing legacy canvas context...');
};

module.exports = CanvasNest;
''', encoding="utf-8")

    test_dir = s1 / "tests"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "test_nest.js").write_text('''const assert = require('assert');
const CanvasNest = require('../src/canvas-nest');

describe('CanvasNest', () => {
    it('initializes properly', () => {
        const nest = new CanvasNest(null);
        assert.ok(nest);
    });
});
''', encoding="utf-8")

    if not (s1 / ".git").exists():
        subprocess.run(["git", "init"], cwd=str(s1), capture_output=True)
        subprocess.run(["git", "config", "user.name", "Arthur Pendelton"], cwd=str(s1), capture_output=True)
        subprocess.run(["git", "config", "user.email", "arthur@spectral.org"], cwd=str(s1), capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(s1), capture_output=True)
        env1 = os.environ.copy()
        env1["GIT_COMMITTER_DATE"] = "2016-04-12T10:00:00"
        env1["GIT_AUTHOR_DATE"] = "2016-04-12T10:00:00"
        subprocess.run(["git", "commit", "-m", "Initial genesis commit: project scaffold and particle engine"], cwd=str(s1), env=env1, capture_output=True)

        (src_dir / "canvas-nest.js").write_text('''// Updated particle collision logic and canvas scaling
CanvasNest.prototype.update = function() {
    // legacy loop
};
''', encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(s1), capture_output=True)
        env2 = os.environ.copy()
        env2["GIT_COMMITTER_DATE"] = "2017-11-20T16:45:00"
        env2["GIT_AUTHOR_DATE"] = "2017-11-20T16:45:00"
        subprocess.run(["git", "commit", "-m", "Final release v1.0.4: retiring active maintenance"], cwd=str(s1), env=env2, capture_output=True)


def create_sample_phantom_cli():
    s2 = SAMPLES_DIR / "phantom-cli-py"
    s2.mkdir(parents=True, exist_ok=True)

    (s2 / "requirements.txt").write_text('''requests==2.18.4
click==6.7
pyyaml==3.12
urllib3==1.22
colorama==0.3.9
''', encoding="utf-8")

    (s2 / "README.md").write_text('''# Phantom CLI

> CLI daemon for logging lingering background processes on developer workstations.

## Installation
```bash
pip install -r requirements.txt
python -m phantom.cli --watch
```

## Status
Development ceased in October 2018. Python 2.7 to 3.5 transition was never finalized.
''', encoding="utf-8")

    (s2 / "LICENSE").write_text('''Apache License 2.0
Copyright 2018 Phantom Systems
''', encoding="utf-8")

    p_dir = s2 / "phantom"
    p_dir.mkdir(exist_ok=True)
    (p_dir / "cli.py").write_text('''import click
import requests

@click.command()
def main():
    """Run Phantom daemon."""
    click.echo("Phantom CLI daemon listening on ghost pipe...")

if __name__ == "__main__":
    main()
''', encoding="utf-8")

    test_p_dir = s2 / "tests"
    test_p_dir.mkdir(exist_ok=True)
    (test_p_dir / "test_cli.py").write_text('''def test_smoke():
    assert True
''', encoding="utf-8")

    if not (s2 / ".git").exists():
        subprocess.run(["git", "init"], cwd=str(s2), capture_output=True)
        subprocess.run(["git", "config", "user.name", "Eleanor Vance"], cwd=str(s2), capture_output=True)
        subprocess.run(["git", "config", "user.email", "eleanor@hillhouse.io"], cwd=str(s2), capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(s2), capture_output=True)
        env3 = os.environ.copy()
        env3["GIT_COMMITTER_DATE"] = "2018-01-15T09:20:00"
        env3["GIT_AUTHOR_DATE"] = "2018-01-15T09:20:00"
        subprocess.run(["git", "commit", "-m", "Initial commit: Phantom daemon CLI structure"], cwd=str(s2), env=env3, capture_output=True)

        (s2 / "requirements.txt").write_text('''requests==2.18.4
click==6.7
pyyaml==3.12
urllib3==1.22
colorama==0.3.9
''', encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(s2), capture_output=True)
        env4 = os.environ.copy()
        env4["GIT_COMMITTER_DATE"] = "2018-10-31T23:59:00"
        env4["GIT_AUTHOR_DATE"] = "2018-10-31T23:59:00"
        subprocess.run(["git", "commit", "-m", "docs: update unmaintained notice and dependency freeze"], cwd=str(s2), env=env4, capture_output=True)


def ensure_samples():
    """Ensures both sample archives exist with verifiable git history."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    create_sample_canvas_nest()
    create_sample_phantom_cli()


if __name__ == "__main__":
    ensure_samples()
    print("All sample archives verified and ready.")
