"""The brain's models, from the simplest to SAINT+ (T040-T043, T049).

Every sequence model takes the same batch (see make_windows) and returns, for each position
t, the logit of "the student answers item t correctly", using only what happened before t.
That shared shape lets one training loop (fit) and one evaluation (predict) serve them all,
which is how the benchmark in T040 compares models fairly.
"""

import math

import numpy as np
import torch
from torch import nn


# ---------------------------------------------------------------------------
# Batches: answer histories cut into fixed-length windows
# ---------------------------------------------------------------------------


def make_windows(df, max_len=100, time_multiplier_fairness=False):
    """Cut each student's answers into windows of `max_len` steps (T048 builds this online).

    Item and concept ids are shifted by +1 so that 0 means padding. Time features are
    log-scaled: elapsed time (how long the answer took) and lag time (time since the
    previous answer). With `time_multiplier_fairness=True`, elapsed time is divided by the
    student's official time multiplier first (T148), so extra time is not read as weakness.
    """
    windows = {k: [] for k in ("item", "kc", "correct", "elapsed", "lag", "mask", "student")}
    has_lag = "lag_s" in df.columns
    for student, g in df.groupby("student", sort=False):
        elapsed = g.elapsed_s.to_numpy(dtype=float)
        if time_multiplier_fairness and "time_multiplier" in g:
            elapsed = elapsed / g.time_multiplier.to_numpy(dtype=float)
        lag = g.lag_s.to_numpy(dtype=float) if has_lag else np.zeros(len(g))
        cols = {
            "item": g.item.to_numpy() + 1,
            "kc": g.kc.to_numpy() + 1,
            "correct": g.correct.to_numpy(),
            "elapsed": np.log1p(elapsed) / 5.0,
            "lag": np.log1p(lag / 60.0) / 8.0,
        }
        for start in range(0, len(g), max_len):
            n = min(max_len, len(g) - start)
            for k, v in cols.items():
                w = np.zeros(max_len, dtype=float)
                w[:n] = v[start : start + n]
                windows[k].append(w)
            m = np.zeros(max_len, dtype=bool)
            m[:n] = True
            windows["mask"].append(m)
            windows["student"].append(np.full(max_len, student))
    out = {k: torch.tensor(np.stack(v)) for k, v in windows.items()}
    for k in ("item", "kc", "correct", "student"):
        out[k] = out[k].long()
    for k in ("elapsed", "lag"):
        out[k] = out[k].float()
    return out


def _batches(windows, batch_size, shuffle, seed=0):
    n = windows["mask"].shape[0]
    order = torch.randperm(n, generator=torch.Generator().manual_seed(seed)) if shuffle else torch.arange(n)
    for i in range(0, n, batch_size):
        idx = order[i : i + batch_size]
        yield {k: v[idx] for k, v in windows.items()}


def fit(model, windows, epochs=5, batch_size=64, lr=2e-3, seed=0, verbose=True):
    """Train any sequence model with binary cross-entropy on the real positions only."""
    torch.manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    history = []
    for epoch in range(epochs):
        model.train()
        total, count = 0.0, 0
        for batch in _batches(windows, batch_size, shuffle=True, seed=seed + epoch):
            logits = model(batch)
            mask = batch["mask"]
            loss = loss_fn(logits[mask], batch["correct"][mask].float())
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += loss.item() * mask.sum().item()
            count += mask.sum().item()
        history.append(total / count)
        if verbose:
            print(f"epoch {epoch + 1}/{epochs}  training loss {history[-1]:.4f}")
    return history


@torch.no_grad()
def predict(model, windows, batch_size=256):
    """Predicted probability of a correct answer and the true answer, for every real position."""
    model.eval()
    probs, labels = [], []
    for batch in _batches(windows, batch_size, shuffle=False):
        p = torch.sigmoid(model(batch))
        probs.append(p[batch["mask"]])
        labels.append(batch["correct"][batch["mask"]])
    return torch.cat(labels).numpy(), torch.cat(probs).numpy()


# ---------------------------------------------------------------------------
# IRT: one number per student (ability) and per item (difficulty) — T043
# ---------------------------------------------------------------------------


class IRT(nn.Module):
    """Two-parameter logistic IRT: P(correct) = sigmoid(a_item * (theta_student - b_item)).

    theta is the student's ability, b the item's difficulty, a its discrimination (how
    sharply the item separates weak from strong students). IRT ignores time and learning:
    a student's ability is the same at answer 1 and answer 100.
    """

    def __init__(self, n_students, n_items):
        super().__init__()
        self.theta = nn.Embedding(n_students, 1)
        self.b = nn.Embedding(n_items, 1)
        self.log_a = nn.Embedding(n_items, 1)
        for e in (self.theta, self.b, self.log_a):
            nn.init.zeros_(e.weight)

    def forward(self, student, item):
        a = self.log_a(item).squeeze(-1).exp()
        return a * (self.theta(student).squeeze(-1) - self.b(item).squeeze(-1))

    def fit(self, student, item, correct, epochs=300, lr=0.05, l2=1e-3):
        student, item = torch.as_tensor(student).long(), torch.as_tensor(item).long()
        y = torch.as_tensor(correct).float()
        opt = torch.optim.Adam(self.parameters(), lr=lr)
        for _ in range(epochs):
            loss = nn.functional.binary_cross_entropy_with_logits(self(student, item), y)
            loss = loss + l2 * (self.theta.weight.pow(2).mean() + self.log_a.weight.pow(2).mean())
            opt.zero_grad()
            loss.backward()
            opt.step()
        return loss.item()

    def item_params(self):
        return self.b.weight.detach().squeeze(-1).numpy(), self.log_a.weight.detach().squeeze(-1).exp().numpy()


def estimate_ability(items, correct, b, a, prior_sd=1.0):
    """Cold start (T043): a new student's ability from a few answers, with known item parameters.

    Bayes on a grid: start from a normal prior (most students are average) and multiply by
    the likelihood of each answer. Returns the posterior mean and standard deviation; the
    standard deviation shrinks as answers come in.
    """
    grid = np.linspace(-4, 4, 401)
    log_post = -0.5 * (grid / prior_sd) ** 2
    for i, y in zip(items, correct):
        p = 1 / (1 + np.exp(-a[i] * (grid - b[i])))
        log_post += np.log(p if y else 1 - p)
    post = np.exp(log_post - log_post.max())
    post /= post.sum()
    mean = (grid * post).sum()
    return mean, math.sqrt(((grid - mean) ** 2 * post).sum())


def item_information(theta, b, a):
    """Fisher information of each item at ability theta: a^2 p (1 - p). The placement test
    (T175) asks the item with the most information, i.e. the one whose answer is least
    predictable for this student right now."""
    p = 1 / (1 + np.exp(-a * (theta - b)))
    return a**2 * p * (1 - p)


# ---------------------------------------------------------------------------
# BKT: a hidden "known / not known" switch per concept — the classic tracer
# ---------------------------------------------------------------------------


class BKT(nn.Module):
    """Bayesian Knowledge Tracing, trained by gradient descent.

    Four numbers per concept: P(known at start), P(learn after each practice), P(guess right
    when not known), P(slip when known). After each answer the probability of "known" is
    updated with Bayes' rule, then the student may learn. Simple and explainable, but it
    treats concepts as independent and ignores time.
    """

    def __init__(self, n_kc):
        super().__init__()
        self.logits = nn.Parameter(torch.tensor([[-0.5, -2.0, -1.0, -2.0]]).repeat(n_kc + 1, 1))

    def params(self):
        p = torch.sigmoid(self.logits)
        return p[:, 0], p[:, 1], 0.5 * p[:, 2], 0.5 * p[:, 3]

    def forward(self, batch):
        init, learn, guess, slip = self.params()
        kc, y = batch["kc"], batch["correct"].float()
        B, L = kc.shape
        known = init.unsqueeze(0).repeat(B, 1)
        logits = []
        for t in range(L):
            k = kc[:, t]
            pk = known.gather(1, k[:, None]).squeeze(1)
            p_correct = pk * (1 - slip[k]) + (1 - pk) * guess[k]
            logits.append(torch.logit(p_correct.clamp(1e-4, 1 - 1e-4)))
            obs = y[:, t]
            post = torch.where(obs > 0.5, pk * (1 - slip[k]) / p_correct, pk * slip[k] / (1 - p_correct))
            new = post + (1 - post) * learn[k]
            real = batch["mask"][:, t]
            known = known.scatter(1, k[:, None], torch.where(real, new, pk)[:, None])
        return torch.stack(logits, 1)


# ---------------------------------------------------------------------------
# DKT: a recurrent network reads the whole history — first deep tracer
# ---------------------------------------------------------------------------


class DKT(nn.Module):
    """Deep Knowledge Tracing (Piech et al., 2015): an LSTM reads (concept, right/wrong) pairs
    one by one and keeps a summary of the student in its hidden state."""

    def __init__(self, n_kc, hidden=64):
        super().__init__()
        self.n_kc = n_kc
        self.embed = nn.Embedding(2 * (n_kc + 1) + 1, hidden)
        self.lstm = nn.LSTM(hidden, hidden, batch_first=True)
        self.out = nn.Linear(hidden, n_kc + 1)

    def forward(self, batch):
        kc, y = batch["kc"], batch["correct"]
        interaction = kc + y * (self.n_kc + 1)
        start = torch.full_like(interaction[:, :1], 2 * (self.n_kc + 1))
        previous = torch.cat([start, interaction[:, :-1]], 1)
        h, _ = self.lstm(self.embed(previous))
        return self.out(h).gather(2, kc[:, :, None]).squeeze(2)

    @torch.no_grad()
    def predict_all(self, batch):
        """Probability of success on every concept at every step: DKT's view of the student."""
        self.eval()
        kc, y = batch["kc"], batch["correct"]
        interaction = kc + y * (self.n_kc + 1)
        h, _ = self.lstm(self.embed(interaction))
        return torch.sigmoid(self.out(h))[:, :, 1:]


# ---------------------------------------------------------------------------
# SAINT+: exercise encoder + response decoder with attention — the Kuizi brain (T042)
# ---------------------------------------------------------------------------


def causal_mask(L):
    """True where attention is forbidden: position t may only look at positions <= t."""
    return torch.triu(torch.ones(L, L, dtype=torch.bool), diagonal=1)


class _Block(nn.Module):
    """Pre-norm transformer block: self-attention, optional cross-attention, feed-forward."""

    def __init__(self, d, heads, dropout, cross):
        super().__init__()
        self.n1 = nn.LayerNorm(d)
        self.self_attn = nn.MultiheadAttention(d, heads, dropout=dropout, batch_first=True)
        self.cross = cross
        if cross:
            self.n2 = nn.LayerNorm(d)
            self.cross_attn = nn.MultiheadAttention(d, heads, dropout=dropout, batch_first=True)
        self.n3 = nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Dropout(dropout), nn.Linear(4 * d, d))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask, memory=None):
        h = self.n1(x)
        x = x + self.drop(self.self_attn(h, h, h, attn_mask=mask, need_weights=False)[0])
        weights = None
        if self.cross:
            h = self.n2(x)
            out, weights = self.cross_attn(h, memory, memory, attn_mask=mask, need_weights=True)
            x = x + self.drop(out)
        x = x + self.drop(self.ff(self.n3(x)))
        return x, weights


class SaintPlus(nn.Module):
    """SAINT+ (Shin et al., 2021), small enough for a laptop.

    Encoder ("what was asked"): item + concept + position embeddings, causal self-attention.
    Decoder ("how the student answered"): previous answer + previous elapsed time + current
    lag time + position, causal self-attention, then cross-attention to the encoder. The
    output at position t is the logit of answering item t correctly. Elapsed time is shifted
    by one step because it is only known after answering; lag time is known when the item is
    shown. The cross-attention weights of the last layer (`last_attention`) show which past
    items weigh on a prediction (T049, T177).
    """

    def __init__(self, n_items, n_kc, d=64, heads=4, layers=2, max_len=100, dropout=0.1, use_time=True):
        super().__init__()
        self.use_time = use_time
        self.item = nn.Embedding(n_items + 1, d, padding_idx=0)
        self.kc = nn.Embedding(n_kc + 1, d, padding_idx=0)
        self.pos = nn.Embedding(max_len, d)
        self.response = nn.Embedding(3, d)  # 0 wrong, 1 right, 2 start
        self.elapsed = nn.Linear(1, d)
        self.lag = nn.Linear(1, d)
        self.encoder = nn.ModuleList(_Block(d, heads, dropout, cross=False) for _ in range(layers))
        self.decoder = nn.ModuleList(_Block(d, heads, dropout, cross=True) for _ in range(layers))
        self.norm = nn.LayerNorm(d)
        self.out = nn.Linear(d, 1)
        self.last_attention = None

    def forward(self, batch):
        item, kc, y = batch["item"], batch["kc"], batch["correct"]
        B, L = item.shape
        pos = self.pos(torch.arange(L))
        mask = causal_mask(L)
        enc = self.item(item) + self.kc(kc) + pos
        for block in self.encoder:
            enc, _ = block(enc, mask)
        prev_y = torch.cat([torch.full_like(y[:, :1], 2), y[:, :-1]], 1)
        dec = self.response(prev_y) + pos
        if self.use_time:
            prev_elapsed = torch.cat([torch.zeros_like(batch["elapsed"][:, :1]), batch["elapsed"][:, :-1]], 1)
            dec = dec + self.elapsed(prev_elapsed[..., None]) + self.lag(batch["lag"][..., None])
        for block in self.decoder:
            dec, weights = block(dec, mask, memory=enc)
        self.last_attention = weights
        return self.out(self.norm(dec)).squeeze(-1)


@torch.no_grad()
def probe(model, history, items, item_kc, max_len=100, lag_s=60.0):
    """SAINT+'s chance of success on each of `items` if it were asked right now (T049, T052).

    `history` is one student's answers (rows of the usual data frame, oldest first); its last
    max_len - 1 answers are kept and each candidate item is placed at the next position.
    Returns the probabilities and, for each item, the last layer's attention weights over the
    history, which say which past answers drove the estimate.
    """
    model.eval()
    h = history.tail(max_len - 1)
    n, B = len(h), len(items)
    lag = h.lag_s.to_numpy() if "lag_s" in h else np.zeros(n)
    batch = {
        "item": torch.tensor(np.r_[h.item.to_numpy(), 0] + 1).repeat(B, 1),
        "kc": torch.tensor(np.r_[h.kc.to_numpy(), 0] + 1).repeat(B, 1),
        "correct": torch.tensor(np.r_[h.correct.to_numpy(), 0]).repeat(B, 1),
        "elapsed": torch.tensor(np.r_[np.log1p(h.elapsed_s.to_numpy()) / 5.0, 0.0], dtype=torch.float32).repeat(B, 1),
        "lag": torch.tensor(
            np.r_[np.log1p(lag / 60.0) / 8.0, np.log1p(lag_s / 60.0) / 8.0], dtype=torch.float32
        ).repeat(B, 1),
        "mask": torch.ones(B, n + 1, dtype=torch.bool),
    }
    batch["item"][:, n] = torch.tensor(np.asarray(items)) + 1
    batch["kc"][:, n] = torch.tensor(np.asarray(item_kc)[np.asarray(items)]) + 1
    p = torch.sigmoid(model(batch))[:, n].numpy()
    attention = model.last_attention[:, n, :n].numpy() if model.last_attention is not None else None
    return p, attention


def typical_items(item_kc, item_difficulty):
    """For each concept, the item whose difficulty is closest to 0: a "typical" question."""
    item_kc, item_difficulty = np.asarray(item_kc), np.asarray(item_difficulty)
    return {
        int(k): int(np.flatnonzero(item_kc == k)[np.argmin(np.abs(item_difficulty[item_kc == k]))])
        for k in np.unique(item_kc)
    }


def probe_mastery(model, history, item_kc, item_difficulty, **kwargs):
    """Mastery per concept (T049): SAINT+'s chance of success on a typical item of each concept.
    Returns {concept: probability} and {concept: attention weights over the history}."""
    typical = typical_items(item_kc, item_difficulty)
    kcs = list(typical)
    p, attention = probe(model, history, [typical[k] for k in kcs], item_kc, **kwargs)
    return (
        {k: float(p[i]) for i, k in enumerate(kcs)},
        {k: attention[i] for i, k in enumerate(kcs)} if attention is not None else None,
    )


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
