#!/usr/bin/env python3
"""
Redrob Intelligent Candidate Discovery & Ranking System
Target Role: Senior AI Engineer (Ranking/Retrieval focus) @ Redrob AI
Location: Pune/Noida, India | 5-9 yrs experience
Pure Python stdlib — no external dependencies.
"""

import csv
import heapq
import json
import time
from datetime import date
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
TODAY = date(2026, 6, 26)
CANDIDATES_FILE = Path(__file__).parent / "candidates.jsonl"
OUTPUT_FILE = Path(__file__).parent / "submission.csv"
TOP_N = 100
BUFFER = 400  # track top-400 during scan, take top-100 at end

# ─── Skill Taxonomies (all lowercase for matching) ────────────────────────────

# MUST-HAVE #1: Embedding / dense retrieval skills
EMBEDDING_SKILLS = frozenset([
    "sentence-transformers", "sentence transformers", "sbert",
    "openai embeddings", "text embeddings", "text embedding",
    "embeddings", "embedding",
    "bge", "e5", "gte", "instructor",
    "bert", "roberta", "distilbert", "albert", "all-minilm",
    "semantic embeddings", "dense embeddings", "vector embeddings",
    "bi-encoder", "cross-encoder",
    "dense retrieval", "dpr", "dense passage retrieval",
    "word2vec", "glove", "fasttext", "word embeddings",
    "ada-002", "text-embedding-ada-002",
    "contrastive learning",
    "clip", "colbert",
])

# MUST-HAVE #2: Vector database / ANN search
VECTOR_DB_SKILLS = frozenset([
    "pinecone", "weaviate", "qdrant", "milvus", "chroma", "chromadb",
    "opensearch", "elasticsearch", "faiss", "annoy", "scann",
    "pgvector", "vespa", "zilliz",
    "vector search", "vector store", "vector database", "vector db",
    "approximate nearest neighbor", "ann", "ann index", "hnsw", "ivf",
    "semantic search engine", "knn search", "knn",
    "redis vector", "redis search",
])

# MUST-HAVE #3: Evaluation / ranking metrics
EVAL_SKILLS = frozenset([
    "ndcg", "mrr", "map",
    "mean average precision", "mean reciprocal rank",
    "evaluation framework", "ranking evaluation", "offline evaluation",
    "a/b testing", "ab testing", "a/b test",
    "information retrieval metrics", "ir metrics",
    "recall@k", "precision@k", "p@10", "p@k",
    "search evaluation", "ranking metrics",
    "online evaluation", "offline-to-online",
    "search quality", "relevance evaluation",
])

# MUST-HAVE #4: Python
PYTHON_SKILLS = frozenset(["python", "python3", "python 3"])

# NICE-TO-HAVE: LLM fine-tuning
FINETUNE_SKILLS = frozenset([
    "lora", "qlora", "peft",
    "fine-tuning llms", "finetuning llms", "llm fine-tuning",
    "fine-tuning", "finetuning",
    "instruction tuning", "rlhf", "dpo", "sft",
    "supervised fine-tuning", "parameter-efficient fine-tuning",
    "full fine-tuning",
])

# NICE-TO-HAVE: Learning-to-rank
LTR_SKILLS = frozenset([
    "learning to rank", "learning-to-rank", "ltr",
    "lambdarank", "listnet", "ranknet", "rankboost",
    "xgboost ranking", "neural ranking",
    "pointwise ranking", "pairwise ranking", "listwise ranking",
])

# NICE-TO-HAVE: NLP / Information Retrieval
NLP_IR_SKILLS = frozenset([
    "nlp", "natural language processing",
    "information retrieval", "ir",
    "semantic search",
    "rag", "retrieval augmented generation", "retrieval-augmented generation",
    "bm25", "tfidf", "tf-idf", "bm-25",
    "text ranking", "re-ranking", "reranking", "llm reranking",
    "hybrid search", "sparse retrieval",
    "question answering", "qa",
    "text classification", "named entity recognition", "ner",
    "transformers", "hugging face", "huggingface",
    "llm", "large language models",
    "gpt", "chatgpt",
    "retrieval", "search ranking", "document ranking",
    "passage retrieval", "document retrieval",
])

# NICE-TO-HAVE: ML Frameworks
ML_SKILLS = frozenset([
    "pytorch", "tensorflow", "jax", "keras",
    "scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
    "mlflow", "wandb", "weights & biases",
    "hugging face", "huggingface", "transformers",
    "ray", "dask",
])

# NICE-TO-HAVE: MLOps / Production systems
MLOPS_SKILLS = frozenset([
    "docker", "kubernetes", "k8s",
    "triton", "onnx", "torchserve", "bentoml",
    "model serving", "model deployment", "inference optimization",
    "distributed training", "distributed inference",
    "quantization", "distillation", "pruning",
    "mlflow", "kubeflow", "airflow",
    "apache spark", "pyspark",
    "ray serve", "seldon", "bento",
])

# DISQUALIFIERS: CV / Vision specialists (only penalized if no NLP/IR bridge)
DISQUAL_VISION = frozenset([
    "computer vision", "image classification",
    "object detection", "image segmentation",
    "convolutional neural network", "cnn", "resnet", "vgg", "yolo",
    "opencv", "image recognition", "face recognition",
    "image processing", "image captioning",
])

# DISQUALIFIERS: Speech / Audio specialists
DISQUAL_SPEECH = frozenset([
    "speech recognition", "speech processing", "asr",
    "tts", "text-to-speech", "speech synthesis",
    "speech-to-text", "stt", "audio processing",
    "speaker recognition", "speaker diarization",
    "whisper",
])

# DISQUALIFIERS: Robotics
DISQUAL_ROBOTICS = frozenset([
    "robotics", "autonomous vehicles", "lidar", "slam",
    "ros", "robot operating system", "path planning",
    "point cloud", "autonomous driving",
])

# Proficiency → weight
PROF_W = {"expert": 1.0, "advanced": 0.80, "intermediate": 0.55, "beginner": 0.25}

# Big Indian IT consulting firms (red flag if ALL roles are here)
CONSULTING_CO = frozenset([
    "wipro", "tcs", "tata consultancy", "tata consultancy services",
    "infosys", "hcl", "hcl technologies",
    "accenture", "cognizant", "capgemini",
    "tech mahindra", "mphasis", "hexaware",
    "mindtree", "ltimindtree", "l&t infotech",
    "dxc technology", "atos", "birlasoft",
])

# Good title keywords
GOOD_TITLE_KW = [
    "ai engineer", "ml engineer", "machine learning engineer",
    "nlp engineer", "search engineer", "ranking engineer",
    "applied scientist", "applied machine learning", "applied ai",
    "research scientist", "ai researcher", "ml researcher",
    "deep learning engineer", "data scientist", "staff data scientist",
    "retrieval engineer", "information retrieval",
    "senior engineer", "staff engineer", "principal engineer",
]

# Clearly irrelevant titles
BAD_TITLE_KW = [
    "hr manager", "human resources", "talent acquisition",
    "accountant", "finance manager", "chartered accountant",
    "civil engineer", "structural engineer",
    "mechanical engineer", "hardware engineer",
    "content writer", "copywriter", "technical writer",
    "marketing manager", "digital marketing", "brand manager",
    "sales executive", "sales manager", "business development",
    "customer support", "customer service", "customer success",
    "graphic designer", "ui designer", "product designer",
    "operations manager", "operations head",
]

# Career text keywords to supplement skill lists
EMBED_TEXT_KW = [
    "embedding", "sentence-transformer", "sentence_transformer",
    "sbert", "word2vec", "fasttext", "bge", "dense retrieval",
    "bi-encoder", "cross-encoder", "semantic similarity",
    "openai embed", "vector represent", "text-embedding",
]

VECTORDB_TEXT_KW = [
    "pinecone", "weaviate", "qdrant", "milvus", "faiss", "chroma",
    "elasticsearch", "opensearch", "pgvector", "vespa",
    "vector store", "vector db", "ann index", "hnsw",
    "approximate nearest neighbor", "knn search", "vector search",
]

EVAL_TEXT_KW = [
    "ndcg", "mrr", "mean average precision", "a/b test", "ab test",
    "ranking metric", "evaluation framework", "offline eval",
    "recall@", "precision@", "search quality", "relevance judge",
    "offline-to-online",
]

# Must-have count → score gate multiplier
MH_MULT = {0: 0.10, 1: 0.30, 2: 0.56, 3: 0.78, 4: 1.00}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(str(s))
    except (ValueError, TypeError):
        return None


def days_ago(date_str):
    d = parse_date(date_str)
    return max(0, (TODAY - d).days) if d else 9999


def skill_quality(skill):
    """Single-skill quality score 0-1 (proficiency × duration × endorsements)."""
    prof = PROF_W.get(skill.get("proficiency", "intermediate"), 0.55)
    dur = min(skill.get("duration_months", 0), 60) / 60.0
    end = min(skill.get("endorsements", 0), 40) / 40.0
    return 0.50 * prof + 0.30 * dur + 0.20 * end


def best_in_set(skills, target_set):
    """
    Returns (matched: bool, score: float) for candidate's skills vs a target set.
    Score accounts for quality of best match + bonus for multiple matches.
    """
    best = 0.0
    count = 0
    for s in skills:
        if s["name"].lower().strip() in target_set:
            q = skill_quality(s)
            best = max(best, q)
            count += 1
    if count == 0:
        return False, 0.0
    bonus = min(0.15, (count - 1) * 0.07)
    return True, min(1.0, best + bonus)


def text_has(text_lower, keywords):
    return any(kw in text_lower for kw in keywords)


# ─── Honeypot Detection ───────────────────────────────────────────────────────

def is_honeypot(candidate):
    """Detect impossible/fabricated profiles."""
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    education = candidate.get("education", [])

    # Check 1: current job duration claimed > actual elapsed months
    for job in career:
        if job.get("is_current"):
            start = parse_date(job.get("start_date"))
            if start:
                actual_months = max(0, (TODAY - start).days / 30.44)
                claimed = job.get("duration_months", 0)
                if claimed > actual_months + 6:   # 6-month tolerance
                    return True

    # Check 2: sum of all tenures wildly exceeds claimed total experience
    total_tenure = sum(j.get("duration_months", 0) for j in career)
    claimed_yrs = profile.get("years_of_experience", 0)
    if total_tenure > (claimed_yrs * 12 + 12) * 2.5:
        return True

    # Check 3: career start before FIRST degree (min end year) by >12 years.
    # Only catch extreme impossibilities; postgrad while working is very common in India.
    # Use min_end (earliest degree) and a wide tolerance to avoid false positives.
    if education:
        min_end = min((e.get("end_year", 2100) for e in education), default=2100)
        if min_end < 2100:
            implied_start_year = 2026 - claimed_yrs
            if implied_start_year < min_end - 12:  # Started working 12+ yrs before graduating
                return True

    return False


# ─── Skills Scoring ───────────────────────────────────────────────────────────

def score_skills(skills, career_text_lower, signals):
    """Returns dict with must-have / nice-to-have breakdown."""
    # Must-have #1: Embeddings
    emb_m, emb_s = best_in_set(skills, EMBEDDING_SKILLS)
    if not emb_m and text_has(career_text_lower, EMBED_TEXT_KW):
        emb_m, emb_s = True, 0.30  # text evidence only → partial credit

    # Check skill assessment scores for embedding-adjacent skills
    assess = signals.get("skill_assessment_scores", {})
    for k, v in assess.items():
        kl = k.lower()
        if any(kw in kl for kw in ["embed", "nlp", "retrieval", "search"]):
            emb_s = max(emb_s, v / 100.0 * 0.5)  # up to 0.5 from assessment
            emb_m = emb_m or (v > 50)

    # Must-have #2: Vector databases
    vdb_m, vdb_s = best_in_set(skills, VECTOR_DB_SKILLS)
    if not vdb_m and text_has(career_text_lower, VECTORDB_TEXT_KW):
        vdb_m, vdb_s = True, 0.30

    # Must-have #3: Evaluation frameworks
    ev_m, ev_s = best_in_set(skills, EVAL_SKILLS)
    ev_text_kws = []
    if not ev_m:
        ev_text_kws = [kw for kw in EVAL_TEXT_KW if kw in career_text_lower]
        hits = len(ev_text_kws)
        if hits > 0:
            # Proportional score: deeper evaluation expertise → higher score
            ev_s = 0.15 + min(0.40, hits * 0.07)  # 0.22 for 1 hit, up to 0.55 for 6+
            ev_m = True

    # Must-have #4: Python
    py_m, py_s = best_in_set(skills, PYTHON_SKILLS)
    if not py_m and "python" in career_text_lower:
        py_m, py_s = True, 0.45
    # Infer Python from Python-ecosystem libraries (FAISS, XGBoost, sentence-transformers, etc.)
    PYTHON_INDICATOR_SKILLS = frozenset([
        "pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost", "lightgbm",
        "faiss", "sentence-transformers", "sentence transformers", "hugging face",
        "huggingface", "transformers", "numpy", "pandas", "mlflow", "wandb",
        "weights & biases", "pyspark", "ray", "dask",
    ])
    if not py_m:
        for s in skills:
            if s["name"].lower().strip() in PYTHON_INDICATOR_SKILLS:
                py_m, py_s = True, 0.60
                break

    # Nice-to-haves
    _, ft_s = best_in_set(skills, FINETUNE_SKILLS)
    _, ltr_s = best_in_set(skills, LTR_SKILLS)
    _, nlp_s = best_in_set(skills, NLP_IR_SKILLS)
    _, ml_s = best_in_set(skills, ML_SKILLS)
    _, mlops_s = best_in_set(skills, MLOPS_SKILLS)

    # Disqualifier check: CV/speech specialist without any IR/embedding bridge
    _, dq_vis = best_in_set(skills, DISQUAL_VISION)
    _, dq_sp = best_in_set(skills, DISQUAL_SPEECH)
    _, dq_rob = best_in_set(skills, DISQUAL_ROBOTICS)
    is_specialist = dq_vis > 0.30 or dq_sp > 0.30 or dq_rob > 0.30
    has_bridge = emb_m or vdb_m or nlp_s > 0.15
    disqual = is_specialist and not has_bridge

    mhc = sum([emb_m, vdb_m, ev_m, py_m])

    must_score = (0.40 * emb_s + 0.30 * vdb_s + 0.20 * ev_s + 0.10 * py_s)
    nice_score = (0.30 * ft_s + 0.20 * ltr_s + 0.25 * nlp_s + 0.15 * ml_s + 0.10 * mlops_s)

    # Cache which named skills matched (for reasoning)
    emb_named = [s["name"] for s in skills if s["name"].lower().strip() in EMBEDDING_SKILLS]
    vdb_named = [s["name"] for s in skills if s["name"].lower().strip() in VECTOR_DB_SKILLS]
    ev_named = [s["name"] for s in skills if s["name"].lower().strip() in EVAL_SKILLS]
    ft_named = [s["name"] for s in skills if s["name"].lower().strip() in FINETUNE_SKILLS]

    return dict(
        emb_m=emb_m, emb_s=emb_s,
        vdb_m=vdb_m, vdb_s=vdb_s,
        ev_m=ev_m, ev_s=ev_s,
        py_m=py_m, py_s=py_s,
        must_have_count=mhc, must_score=must_score, nice_score=nice_score,
        ft_s=ft_s, ltr_s=ltr_s, nlp_s=nlp_s,
        disqual=disqual,
        emb_named=emb_named, vdb_named=vdb_named,
        ev_named=ev_named, ft_named=ft_named,
        ev_text_kws=ev_text_kws,
    )


# ─── Experience Scoring ───────────────────────────────────────────────────────

def score_experience(profile, career):
    years = profile.get("years_of_experience", 0)
    title_l = profile.get("current_title", "").lower()

    # Experience band (5-9 ideal for this JD)
    if 5 <= years <= 9:
        yr_s = 1.0
    elif 9 < years <= 11:
        yr_s = 0.87
    elif 3 <= years < 5:
        yr_s = 0.70
    elif 11 < years <= 14:
        yr_s = 0.73
    elif years > 14:
        yr_s = 0.58
    else:
        yr_s = max(0.20, years / 5.0 * 0.65)

    # Current title relevance
    title_s = 0.45
    for kw in GOOD_TITLE_KW:
        if kw in title_l:
            title_s = 0.90
            break
    else:
        for kw in BAD_TITLE_KW:
            if kw in title_l:
                title_s = 0.18
                break

    # Career history analysis
    ml_roles = consulting_roles = tech_roles = 0
    n = len(career)

    for job in career:
        jt = job.get("title", "").lower()
        jc = job.get("company", "").lower()
        ji = job.get("industry", "").lower()

        for kw in GOOD_TITLE_KW:
            if kw in jt:
                ml_roles += 1
                break

        for co in CONSULTING_CO:
            if co in jc:
                consulting_roles += 1
                break

        tech_kws = ["technology", "tech", "software", "saas", "ai", "machine learning",
                    "artificial intelligence", "data", "analytics", "cloud", "startup"]
        if any(k in ji for k in tech_kws) or any(k in jc for k in tech_kws):
            tech_roles += 1

    if n > 0:
        ml_ratio = ml_roles / n
        cons_ratio = consulting_roles / n
        tech_ratio = tech_roles / n
    else:
        ml_ratio = cons_ratio = tech_ratio = 0.0

    traj_s = (
        0.50 * min(1.0, ml_ratio + 0.20) +
        0.30 * min(1.0, tech_ratio) +
        0.20 * (1.0 - cons_ratio)
    )

    cons_penalty = min(0.65, cons_ratio * 0.70)

    return dict(
        yr_s=yr_s, title_s=title_s, traj_s=traj_s,
        cons_penalty=cons_penalty,
        years=years, title=profile.get("current_title", ""),
        ml_roles=ml_roles, n_jobs=n,
    )


# ─── Behavioral Signal Scoring ────────────────────────────────────────────────

def score_signals(signals):
    # Activity / availability
    inactive = days_ago(signals.get("last_active_date"))
    if inactive < 7:
        act_s = 1.0
    elif inactive < 30:
        act_s = 0.88
    elif inactive < 90:
        act_s = 0.65
    elif inactive < 180:
        act_s = 0.38
    else:
        act_s = 0.10

    open_w = signals.get("open_to_work_flag", False)
    avail_s = min(1.0, act_s * (1.12 if open_w else 0.92))

    # Responsiveness
    rr = signals.get("recruiter_response_rate", 0.0)
    rt = signals.get("avg_response_time_hours", 999.0)
    rt_s = (1.0 if rt < 4 else (0.85 if rt < 24 else (0.60 if rt < 72 else (0.38 if rt < 168 else 0.12))))
    resp_s = 0.60 * rr + 0.40 * rt_s

    # GitHub (open-source signal — key for this role)
    gh = signals.get("github_activity_score", -1)
    gh_s = 0.0 if gh < 0 else gh / 100.0

    # Profile quality
    comp_s = signals.get("profile_completeness_score", 50) / 100.0
    ver_s = (
        signals.get("verified_email", False) +
        signals.get("verified_phone", False) +
        signals.get("linkedin_connected", False)
    ) / 3.0

    # Notice period
    notice = signals.get("notice_period_days", 90)
    notice_s = (1.0 if notice <= 15 else (0.90 if notice <= 30 else
                (0.75 if notice <= 60 else (0.55 if notice <= 90 else 0.32))))

    # Reliability signals
    ic = signals.get("interview_completion_rate", 0.5)
    oa = signals.get("offer_acceptance_rate", -1)
    oa_s = 0.5 if oa < 0 else oa

    total = (
        0.25 * avail_s +
        0.22 * resp_s +
        0.18 * gh_s +
        0.12 * comp_s +
        0.08 * ver_s +
        0.08 * notice_s +
        0.04 * ic +
        0.03 * oa_s
    )

    return dict(
        sig_s=total,
        act_s=act_s, resp_rate=rr, gh=gh,
        notice=notice, inactive=inactive,
    )


# ─── Education Scoring ────────────────────────────────────────────────────────

def score_education(education):
    if not education:
        return dict(edu_s=0.30)

    tier_v = {"tier_1": 1.0, "tier_2": 0.80, "tier_3": 0.55, "tier_4": 0.30, "unknown": 0.40}
    cs_fields = [
        "computer science", "computer engineering", "information technology",
        "electrical engineering", "electronics", "data science",
        "statistics", "mathematics", "computational", "software",
    ]

    best = 0.0
    for edu in education:
        tier = tier_v.get(edu.get("tier", "unknown"), 0.40)
        deg = edu.get("degree", "").lower()

        if any(x in deg for x in ["phd", "ph.d", "doctor"]):
            deg_v = 1.0
        elif any(x in deg for x in ["m.tech", "m.sc", "msc", "m.s.", "ms ", "master"]):
            deg_v = 0.85
        elif "mba" in deg:
            deg_v = 0.48
        elif any(x in deg for x in ["b.tech", "b.e.", "b.e ", "btech", "bachelor", "b.sc"]):
            deg_v = 0.68
        else:
            deg_v = 0.52

        field = edu.get("field_of_study", "").lower()
        field_v = 0.82 if any(f in field for f in cs_fields) else 0.44

        best = max(best, 0.40 * tier + 0.35 * deg_v + 0.25 * field_v)

    return dict(edu_s=best)


# ─── Master Score Function ────────────────────────────────────────────────────

def score_candidate(candidate):
    """Return (total_score: float, features: dict)."""
    if is_honeypot(candidate):
        return 0.0, {"honeypot": True}

    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    education = candidate.get("education", [])

    # Build search text from all text fields
    career_text = " ".join(
        j.get("description", "") + " " + j.get("title", "") + " " + j.get("company", "")
        for j in career
    ) + " " + profile.get("summary", "") + " " + profile.get("headline", "")
    ctl = career_text.lower()

    sf = score_skills(skills, ctl, signals)
    ef = score_experience(profile, career)
    sig = score_signals(signals)
    edu = score_education(education)

    # Disqualifier multiplier (specialist with no NLP/IR bridge)
    dq_mult = 0.25 if sf["disqual"] else 1.0

    # Component scores
    skills_comp = 0.55 * sf["must_score"] + 0.45 * sf["nice_score"]
    exp_comp = (
        0.35 * ef["yr_s"] +
        0.40 * ef["title_s"] +
        0.25 * ef["traj_s"]
    ) * (1.0 - ef["cons_penalty"])

    raw = (
        0.42 * skills_comp +
        0.28 * exp_comp +
        0.18 * sig["sig_s"] +
        0.12 * edu["edu_s"]
    )

    # Must-have gate (ensures 4/4 always outranks 3/4, etc.)
    mhm = MH_MULT[sf["must_have_count"]]
    total = max(0.0, min(1.0, raw * mhm * dq_mult))

    return total, {**sf, **ef, **sig, **edu}


# ─── Reasoning Generator ──────────────────────────────────────────────────────

def make_reasoning(candidate, score, f):
    """Grounded 1-2 sentence reasoning referencing actual profile facts and JD requirements."""
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    title = profile.get("current_title", "")
    years = profile.get("years_of_experience", 0)
    rr = signals.get("recruiter_response_rate", 0)
    gh = f.get("gh", -1)
    mhc = f.get("must_have_count", 0)

    # Build specific technical matches for JD must-haves
    jd_matches = []
    emb = f.get("emb_named", [])
    vdb = f.get("vdb_named", [])
    ev = f.get("ev_named", [])
    ft = f.get("ft_named", [])
    ltr = f.get("ltr_s", 0)

    if emb:
        jd_matches.append(f"embeddings ({emb[0]})")
    elif f.get("emb_m"):
        jd_matches.append("embeddings (text evidence)")
    if vdb:
        vdb_str = "/".join(vdb[:2])
        jd_matches.append(f"vector DB ({vdb_str})")
    elif f.get("vdb_m"):
        jd_matches.append("vector DB (text evidence)")
    if f.get("ev_m"):
        if ev:
            jd_matches.append(f"eval ({ev[0]})")
        else:
            ev_kws = f.get("ev_text_kws", [])
            # Show most informative eval keywords found in career text
            ev_display = [k.upper() if k in ("ndcg", "mrr", "map") else k for k in ev_kws[:3]]
            kw_str = ", ".join(ev_display) if ev_display else "NDCG/MRR"
            jd_matches.append(f"eval frameworks ({kw_str} in work history)")
    if ft:
        jd_matches.append(f"LLM fine-tuning ({ft[0]})")
    if ltr > 0.2:
        jd_matches.append("learning-to-rank")

    jd_str = "; ".join(jd_matches[:3]) if jd_matches else "limited JD skill overlap"

    # Signal highlights
    sig_parts = [f"response rate {rr:.2f}"]
    if gh > 0:
        sig_parts.append(f"GitHub {gh:.0f}")
    inactive = f.get("inactive", 0)
    if inactive < 30:
        sig_parts.append("recently active")
    sig_str = ", ".join(sig_parts)

    sentence1 = f"{title} ({years:.1f} yrs): {mhc}/4 JD must-haves — {jd_str}; {sig_str}."

    # Concerns
    concerns = []
    if mhc < 4:
        missing = []
        if not f.get("emb_m"):
            missing.append("no embedding skill")
        if not f.get("vdb_m"):
            missing.append("no vector DB")
        if not f.get("ev_m"):
            missing.append("no eval framework evidence")
        if missing:
            concerns.append(f"gaps: {', '.join(missing)}")
    if f.get("cons_penalty", 0) > 0.30:
        concerns.append("consulting-heavy career (most roles at big IT services firms)")
    if f.get("disqual"):
        concerns.append("CV/speech specialist — limited NLP/IR bridge")
    if inactive > 90:
        concerns.append(f"inactive {inactive}d")
    if f.get("notice", 0) > 90:
        concerns.append(f"notice period {f['notice']}d")
    if years < 4:
        concerns.append(f"below ideal exp band (5-9 yrs, has {years:.1f})")

    if concerns:
        return f"{sentence1} Concerns: {'; '.join(concerns)}."
    return sentence1


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"Redrob Candidate Ranker — {TODAY}")
    print(f"Input:  {CANDIDATES_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Min-heap: (score, cid) — keeps the top-BUFFER highest-scoring candidates
    heap = []
    store = {}  # cid -> (score, candidate, feats)
    total = honeypots = 0

    with open(CANDIDATES_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue

            total += 1
            if total % 20000 == 0:
                print(f"  [{time.time()-t0:.0f}s] {total:,} processed…")

            candidate = json.loads(line)
            score, feats = score_candidate(candidate)

            if feats.get("honeypot"):
                honeypots += 1
                continue

            cid = candidate["candidate_id"]

            if len(heap) < BUFFER:
                heapq.heappush(heap, (score, cid))
                store[cid] = (score, candidate, feats)
            elif score > heap[0][0]:
                _, old_cid = heapq.heapreplace(heap, (score, cid))
                del store[old_cid]
                store[cid] = (score, candidate, feats)

    elapsed = time.time() - t0
    print(f"\n  [{elapsed:.1f}s] Scanned {total:,} candidates. Honeypots filtered: {honeypots}")

    # Sort: rounded score DESC, then candidate_id ASC for tie-breaking.
    # We round to match CSV output precision (4 decimal places) so ties are broken correctly.
    ranked = sorted(store.values(), key=lambda x: (-round(x[0], 4), x[1]["candidate_id"]))
    top100 = ranked[:TOP_N]

    # Write CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (score, cand, feats) in enumerate(top100, 1):
            reasoning = make_reasoning(cand, score, feats)
            writer.writerow([cand["candidate_id"], rank, f"{score:.4f}", reasoning])

    # Verify non-increasing scores (safety check)
    scores = [s for s, _, _ in top100]
    monotone = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))

    print(f"\nTop 15 candidates:")
    print(f"{'#':>3}  {'ID':<15} {'Title':<35} {'Yrs':>4}  {'Score':>7}  {'MH':>3}  {'emb':>5} {'vdb':>5} {'ev':>5} {'sig':>5}")
    print("-" * 100)
    for rank, (score, cand, f) in enumerate(top100[:15], 1):
        p = cand["profile"]
        print(
            f"{rank:>3}  {cand['candidate_id']:<15}"
            f" {p['current_title'][:35]:<35}"
            f" {p['years_of_experience']:>4.1f}"
            f"  {score:>7.4f}"
            f"  {f.get('must_have_count')}/4"
            f"  {f.get('emb_s', 0):>5.2f}"
            f" {f.get('vdb_s', 0):>5.2f}"
            f" {f.get('ev_s', 0):>5.2f}"
            f" {f.get('sig_s', 0):>5.2f}"
        )

    print(f"\nScores non-increasing: {monotone}")
    print(f"Total time: {time.time()-t0:.1f}s")
    print(f"Submission written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
