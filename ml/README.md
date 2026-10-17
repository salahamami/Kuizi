# Kuizi brain (`ml/`)

Python environment for the knowledge-tracing work: the brain walkthrough notebooks (T238), the model benchmark (T040), pyKT (T041), SAINT+ (T042) and the IRT cold start (T043).

```bash
make ml-setup   # installs Python 3.12, PyTorch (CPU) and the libraries below with uv
make ml-lab     # opens JupyterLab
```

Start with the [brain walkthrough](../docs/brain/README.md): ten notebooks in `notebooks/`, built on the small library in `kuizi_brain/`.

Experiments are logged to the local MLflow server (`MLFLOW_TRACKING_URI` in `.env`, started by `make up`).

Only public datasets (ASSISTments, EdNet) and synthetic data go here. Never put real student data in this folder or in a notebook.
