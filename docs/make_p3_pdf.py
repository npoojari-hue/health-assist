# builds P3_CodeHealthCrew.pdf with reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether)

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["Normal"], fontName="Times-Roman", fontSize=10.5, leading=13.2, spaceAfter=5)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Times-Bold", fontSize=13.5, spaceBefore=9, spaceAfter=4, textColor=colors.HexColor("#1d3b66"))
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Times-Bold", fontSize=11, spaceBefore=5, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=8.8, leading=10.6, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Times-Bold")
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2)
cap = ParagraphStyle("cap", parent=body, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
ctr = ParagraphStyle("ctr", parent=body, alignment=TA_CENTER, fontSize=12, leading=16)
ref = ParagraphStyle("ref", parent=body, fontSize=9, leading=11, leftIndent=18, firstLineIndent=-18, spaceAfter=2)

P = lambda t, s=body: Paragraph(t, s)
B = lambda t: Paragraph(t, bullet, bulletText="\u2022")


def table(rows, widths, header=True):
    data = [[Paragraph(str(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#888888")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce6f2")))
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8.5)
    canvas.drawString(0.8 * inch, 0.5 * inch, "COMP 4310 - P3: Requirements and Design - Code Health Crew")
    canvas.drawRightString(7.7 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


s = []
# ---------------- cover ----------------
s += [Spacer(1, 1.3 * inch), P("<b>P3: Requirements and Design</b>", ParagraphStyle("t", parent=ctr, fontSize=22, leading=28)),
      Spacer(1, 10), P("<b>HealthAssist: A Consent-Based Health Habits Assistant Grounded in Canadian and WHO Guidance</b>", ctr),
      Spacer(1, 30), P("COMP 4310 - Web Health Informatics", ctr), P("Department of Computer Science, Lakehead University", ctr),
      Spacer(1, 30), P("<b>Team:</b> Code Health Crew", ctr),
      P("Nihar Poojari (1200112) - npoojari@lakeheadu.ca", ctr),
      P("Dinesh Reddy Morthala (1237037) - dmorthal@lakeheadu.ca", ctr), Spacer(1, 20),
      P("Repository: https://github.com/npoojari-hue/health-assist", ctr), P("Submission date: November 2026", ctr), PageBreak()]

# ---------------- 1 ----------------
s.append(P("1. Refined Project Direction", h1))
s.append(P("<b>Problem.</b> Adults in Canada increasingly ask general AI chatbots everyday health questions about sleep, activity, nutrition and hydration. "
           "The answers sound confident and caring, which is why people prefer them [3], but they cannot be checked, may be made up, may be alarming in tone, and usually need personal data to be sent to a third-party cloud service [1], [2]. "
           "Generic guideline pages, on the other hand, are hard for a person to relate to their own routine [8]."))
s.append(P("<b>Gap found in P2.</b> Our review of 10 works showed four gaps: (1) hallucination and missing citations in consumer AI, (2) over-medicalized and alarming tone, "
           "(3) privacy leaks in cloud-based health apps, and (4) guidelines that are too static while tracking apps are too tedious. We also saw that safety and refusal behaviour is rarely evaluated "
           "in health chatbots [6], [7], and that language models are unreliable at arithmetic, so guideline comparisons should not be left to the model."))
s.append(P("<b>Contribution.</b> We will deliver (a) a working HealthAssist prototype and (b) a small, repeatable evaluation of it. The prototype separates three jobs: "
           "<i>Python rules</i> compare the user's habits with the Canadian 24-Hour Movement Guidelines, <i>RAG over a curated Canadian and WHO knowledge base</i> [4], [5] supplies the facts and the visible sources, "
           "and a <i>locally run open model</i> (Llama or Gemma) only rewrites the retrieved text in calm, plain language. A safety filter and a citation check sit before and after the model, and the system declines when sources are insufficient."))
s.append(P("<b>Changes since P1.</b>"))
for t in ["Habit comparison is now done by deterministic Python rules, not by the model (from the P2 finding on LLM arithmetic).",
          "Only the rule results (short habit notes) are sent to the model, not the raw profile, to minimize data exposure.",
          "Emergency and medical redirection now uses Canadian contacts: 9-1-1, Health811 (8-1-1, Ontario) and 9-8-8 for mental health crises.",
          "Hydration has no exact daily number in Canada's Food Guide [13], so it is answered by retrieval only and is not part of the numeric comparison. Sleep targets depend on age (7-9 h for 18-64, 7-8 h for 65+).",
          "RAGAS-style metrics [12] are now a supplement; the main evaluation is our own labelled test set scored by us in two separate passes plus a few peer raters, because a small local model as judge can be biased (see P2).",
          "The first prototype is a single-user local app (no login) to keep the scope realistic for two people."]:
    s.append(B(t))

# ---------------- 2 ----------------
s.append(P("2. Functional and Non-Functional Requirements", h1))
s.append(P("The only actor is the <b>user</b> (an adult in Canada); the <b>system</b> and the <b>evaluators</b> (the team and a few peer raters) are secondary actors. "
           "Each requirement below is written so that it can be checked by a test or a demonstration."))
fr = [["ID", "Requirement", "Actor", "How it is verified"],
      ["FR1", "The system shall show a plain-language consent notice and shall not store any profile, question or history until the user accepts it.", "User", "API test: calls return 403 before consent"],
      ["FR2", "The user shall be able to create, view and edit an optional habit profile (age, sleep, active minutes, strength days, sitting and screen hours) with range-checked fields.", "User", "Unit tests on validation; UI walkthrough"],
      ["FR3", "The system shall compare the profile with Canadian guideline values using deterministic rules and show a calm status per topic (meets / below / above / not shared).", "System", "pytest boundary cases (e.g. 150 min, age 65 sleep)"],
      ["FR4", "The system shall answer wellness questions using only passages retrieved from the curated Canadian/WHO knowledge base and shall display the source title, organization and link.", "User, System", "Source-hit rate on labelled test cases"],
      ["FR5", "Before retrieval, the system shall detect emergency, self-harm, diagnosis, medication and treatment requests and reply with a calm redirection (9-1-1, 8-1-1, 9-8-8).", "System", "Out-of-scope test cases; target 100% redirected"],
      ["FR6", "The system shall decline to answer when no passage is relevant enough, or when the generated answer cites a passage that was not retrieved.", "System", "Unanswerable test cases; citation check unit tests"],
      ["FR7", "The system shall keep a history of questions and answers and let the user rate each answer (1-5).", "User", "API and UI tests"],
      ["FR8", "The user shall be able to delete all stored data (consent, profile, history, feedback) with one action.", "User", "Test that all tables are empty afterwards"]]
s.append(table(fr, [0.4 * inch, 3.55 * inch, 0.8 * inch, 2.15 * inch]))
s.append(P("Table 1. Functional requirements.", cap))
nfr = [["ID", "Requirement", "Measure"],
       ["NFR1 Privacy / security", "Profile fields, questions and answers are encrypted at rest (Fernet, AES-based); the LLM runs locally; no personal data in logs; no outside AI service is called.", "Database inspection shows ciphertext; network check shows only localhost traffic"],
       ["NFR2 Safety and tone", "Answers use calm, optional wording, never diagnose, and always carry the \"not medical advice\" disclaimer.", "Tone score of at least 4/5 on average (own two passes + peers); 0 diagnoses in test set"],
       ["NFR3 Traceability / accuracy", "Every displayed claim comes from a cited, retrieved passage; numeric guideline outputs are exactly the rule values.", "Citation correctness of at least 90%; 100% rule agreement"],
       ["NFR4 Performance", "A typical answer is returned in a reasonable time on a student laptop with an 8B model, and the UI shows a progress message while waiting.", "Median response time of 30 s or less (to be confirmed on our hardware)"],
       ["NFR5 Usability / maintainability", "Simple one-page interface with readable text; knowledge base can be updated by adding a text file and re-running the ingest script; code covered by unit tests.", "Small usability check with 3-5 peers; ingest runs in one command"]]
s.append(table(nfr, [1.2 * inch, 3.3 * inch, 2.4 * inch]))
s.append(P("Table 2. Non-functional requirements.", cap))
s.append(P("<b>Link to the contribution.</b> FR3 and NFR3 answer the \"LLMs should not do the math\" finding; FR4, FR6 and NFR3 answer the hallucination and missing-citation gap; FR5 and NFR2 answer the alarming-tone gap and the missing safety evaluation; "
           "FR1, FR8 and NFR1 answer the privacy gap; and FR2 with FR3 answer the \"guidelines are too static\" gap."))

# ---------------- 3 ----------------
s.append(P("3. System Design", h1))
s.append(P("HealthAssist is a three-tier web application that runs entirely on one machine (Figure 1). The <b>React</b> front end handles consent, the profile form, chat, sources and history. "
           "The <b>FastAPI</b> back end exposes the REST routes (<font face='Courier' size='9'>/api/consent, /profile, /ask, /history, /feedback, /my-data</font>) and runs the question pipeline. "
           "<b>SQLite</b> stores consent, profile, history and feedback with field-level encryption. <b>ChromaDB</b> stores the embedded knowledge-base chunks together with their source metadata, and <b>Ollama</b> serves the local model."))
s.append(Image("docs/architecture.png", width=6.5 * inch, height=6.5 * inch * 5.9 / 10.0 * 0.97))
s.append(P("Figure 1. System architecture and data flow.", cap))
comp = [["Component", "Responsibility", "Receives / sends"],
        ["React front end", "Consent screen, habit form, question box, answer with sources, ratings, history, delete button.", "JSON over HTTP to the back end"],
        ["API layer (FastAPI)", "Validates input (Pydantic), checks consent, calls the pipeline, saves history.", "Front end requests; DB; pipeline"],
        ["Safety filter", "Pattern-based detection of emergency, self-harm, diagnosis, medication and treatment requests before any retrieval.", "Question text in; redirect message or \"safe\" out"],
        ["Guideline rules", "Compare the profile with reference values (sleep by age, 150 min activity, 2 strength days, 8 h sitting, 3 h screen) and write calm messages.", "Profile in; list of status results out"],
        ["Knowledge base + retrieval", "Cleaned and chunked Canadian/WHO notes stored with title, organization and URL; returns passages only below a distance threshold.", "Question in; relevant passages (or none) out"],
        ["Local LLM (Ollama)", "Writes a short answer using only the numbered passages and the habit notes, adding [S1]-style tags. Not a source of facts.", "Prompt in; text out"],
        ["Citation check", "Rejects answers with no tags or tags that were not retrieved; builds the final source list.", "Answer and passages in; accepted answer or decline"],
        ["Encrypted database", "Stores personal data as ciphertext; supports delete-all.", "Back end only"]]
s.append(table(comp, [1.35 * inch, 3.6 * inch, 1.95 * inch]))
s.append(P("Table 3. Components and responsibilities.", cap))
s.append(P("<b>Information flow for a question (Figure 2).</b> (1) The user submits a question. (2) The safety filter runs first; unsafe requests get a calm redirection and stop here. "
           "(3) The retrieval step searches the knowledge base; if no passage is close enough the system declines. (4) The rules turn the saved profile into short habit notes. "
           "(5) The local model writes an answer from the passages and notes. (6) The citation check verifies the tags; failures lead to a decline instead of an unsupported answer. "
           "(7) The answer, sources and disclaimer are shown and saved (encrypted) in the history."))
s.append(Image("docs/workflow.png", width=6.5 * inch, height=6.5 * inch * 3.3 / 10.0))
s.append(P("Figure 2. Question workflow with the three refusal paths.", cap))
s.append(P("<b>Role of AI and its limits.</b> AI is used in two places: embeddings for retrieval, and a language model for wording. The model never calculates, never decides what is safe, and its output is not shown "
           "unless it cites retrieved passages. Safety and arithmetic are rule-based on purpose so they can be tested. "
           "<b>Data model.</b> Four tables: <i>consent</i>, <i>profile</i> (one encrypted JSON field), <i>history</i> (encrypted question and answer plus source list) and <i>feedback</i>."))

# ---------------- 4 ----------------
s.append(P("4. Technology Selection and Justification", h1))
tech = [["Technology", "Role in the project", "Why it fits our requirements"],
        ["React (Vite)", "Single-page interface", "Component structure suits the consent / form / chat / history screens; Vite gives a quick dev setup; we already know it."],
        ["Python + FastAPI + Pydantic [16]", "REST back end and pipeline", "Same language as the AI libraries; automatic input validation supports FR2; built-in API docs help testing."],
        ["ChromaDB + LangChain text splitter [16]", "Vector index and chunking", "Runs locally with no server (NFR1) and keeps source metadata for citations (FR4). The splitter gives overlapping chunks so guideline sentences are not cut apart."],
        ["Ollama with Llama 3.1 8B and Gemma 2 9B [15]", "Local language model", "Keeps profile data on the machine (NFR1) and gives two open models for the comparison in our evaluation; 8-9B models fit student hardware."],
        ["SQLite + cryptography (Fernet)", "Encrypted storage", "Zero-setup database suitable for one local user; Fernet provides authenticated, AES-based encryption for each personal field."],
        ["Plain Python rules", "Guideline comparison and safety patterns", "Predictable and unit-testable (FR3, FR5); avoids model arithmetic errors."],
        ["pytest", "Automated tests", "Verifies rules, safety patterns and citation checks on every change."],
        ["Evaluation scripts (JSON + CSV), optional RAGAS [12]", "Test cases and scoring sheets", "Our own labelled set is transparent; RAGAS can add faithfulness and relevance scores if time allows."],
        ["GitHub", "Version control and collaboration", "Shared repository, commit history shows each member's work."],
        ["Data: Health Canada, PHAC, Canada's Food Guide, CSEP, WHO [9], [10], [13], [14]", "Knowledge base", "Authoritative, public guidance. Terms of use will be checked, and we store short attributed excerpts with links."]]
s.append(table(tech, [1.6 * inch, 1.5 * inch, 3.8 * inch]))
s.append(P("Table 4. Technology choices. We use synthetic profiles and questions only; no real patient data.", cap))
s.append(P("We chose these tools because they meet the privacy and traceability requirements with free, local software, and RAG is known to improve medical answer accuracy only when the retrieved text is clean and relevant [5], which is why we curate the knowledge base. A cloud LLM API would be easier to use but would send health habits to a third party, which conflicts with NFR1."))

# ---------------- 5 ----------------
s.append(P("5. Implementation and Evaluation Plan", h1))
s.append(P("<b>Status.</b> The repository already contains a first version of the back end modules (consent, encrypted storage, rules, safety filter, retrieval, pipeline), a basic React interface, a starter knowledge base, "
           "21 passing automated tests and an evaluation script. The remaining work is to verify and extend the knowledge base, connect and tune the models, finish the interface, and run the evaluation. "
           "Dinesh is the main developer and owns all tasks below; the plan is kept narrow for that reason."))
plan = [["Week", "Tasks", "Owner", "Output"],
        ["Nov 9-15", "Verify knowledge-base notes against official pages and add source details; check terms of use; finalize encrypted DB and consent/profile API; React skeleton", "Dinesh", "Working consent + profile flow"],
        ["Nov 16-22", "Index and retrieval tuning (chunk size, threshold); guideline rules and tests; safety patterns; profile form and comparison display", "Dinesh", "Retrieval and rules tested"],
        ["Nov 23-29", "Ollama integration, prompt, citation check; question page, sources, history, feedback; end-to-end test. <b>P4 prototype</b> (confirm date on D2L)", "Dinesh", "P4 working prototype"],
        ["Nov 30-Dec 6", "Write 60-70 synthetic test cases and 10 profiles; run Llama vs Gemma and RAG vs no-RAG; score in two separate passes, with peers rating a sample", "Dinesh", "Results CSV files"],
        ["Dec 7-13", "Analyze results, resolve scoring disagreements, small usability check (3-5 peers), fix issues, final report and demo", "Dinesh", "Final report and demo"]]
s.append(table(plan, [0.8 * inch, 3.6 * inch, 1.5 * inch, 1.0 * inch]))
s.append(P("Table 5. Task allocation and timeline (dates to be aligned with the D2L schedule).", cap))
s.append(P("<b>Deliverables.</b> <i>P4:</i> running prototype (consent, profile, rule comparison, safety redirection, RAG answers with sources, history), the unit tests, and an initial evaluation on a small test set. "
           "<i>Final:</i> complete application, full evaluation with Llama vs Gemma and RAG vs no retrieval, usability findings, limitations section, and the GitHub repository with README."))
s.append(P("<b>Evaluation plan.</b> We will use about 10 synthetic profiles and 60-70 test cases in four groups: in-scope questions with labelled supporting passages, profile-based cases with expected guideline outcomes, "
           "out-of-scope requests, and questions the knowledge base does not cover. For each test case we record:"))
ev = [["Measure", "How", "Target"],
      ["Outcome correctness (answered / redirected / declined)", "Automatic comparison with the expected outcome", "100% redirect on out-of-scope; at least 90% decline on unanswerable"],
      ["Retrieval relevance (source hit)", "Is the labelled source among the retrieved/cited passages?", "At least 85%"],
      ["Faithfulness and citation correctness", "Own two scoring passes (a few days apart) plus a peer check on a sample verify that each claim is supported by the displayed source", "At least 90% correct citations"],
      ["Guideline agreement", "Compare displayed status with the expected rule outcome", "100%"],
      ["Tone (calm, non-pressuring)", "1-5 rubric, scored in two separate passes; peers rate a sample; differences are reviewed", "Average at least 4"],
      ["Model comparison", "Llama vs Gemma, and RAG vs no retrieval, on the same cases", "Report differences; no fixed target"],
      ["Privacy and function checks", "Inspect database for plaintext; check logs; test consent gate and delete-all", "All pass"]]
s.append(table(ev, [2.2 * inch, 3.0 * inch, 1.7 * inch]))
s.append(P("Table 6. Evaluation measures. The no-retrieval baseline uses synthetic, non-personal questions only.", cap))
s.append(P("<b>Risks and mitigation.</b>"))
risks = [["Risk", "Mitigation"],
         ["Local models are slow or weak on our laptops, and the two models may behave differently.", "Use quantized 8-9B models, short prompts and small top-k; measure response time early; if too slow, evaluate on a shorter test set or one model first."],
         ["Retrieval returns weak or noisy passages, or the knowledge base misses a topic, causing wrong or too many declines.", "Keep the knowledge base small and curated; tune chunk size and distance threshold on a development subset; add missing notes; the citation check blocks unsupported answers."],
         ["Source terms of use or copying limits (we paraphrase and attribute short excerpts).", "Review terms in the first week; store short excerpts with links; keep a source list in the repo."],
         ["Keyword-based safety filter misses some phrasings or blocks harmless questions.", "Test with varied wording, report false positives/negatives in the evaluation, and state this limitation clearly."],
         ["Limited time and one main developer.", "Keep personalization narrow (sleep, activity, sitting); treat nutrition depth and RAGAS as optional extras."]]
s.append(table(risks, [3.0 * inch, 3.9 * inch]))
s.append(P("Table 7. Main risks.", cap))
s.append(P("<b>Limitations.</b> HealthAssist is an informational prototype, not a medical device. Encryption at rest is not end-to-end encryption (the server must read the profile) and is not a legal PIPEDA compliance review [11]. "
           "Real patient data, symptom checking, medication advice, other languages and public deployment are out of scope."))

# ---------------- references ----------------
s.append(P("References", h1))
refs = ["[1] G. Eysenbach and C. Kohler, \"How do consumers search for and appraise health information on the world wide web?,\" <i>BMJ</i>, vol. 324, no. 7337, pp. 573-577, 2002.",
        "[2] Z. Ji et al., \"Survey of hallucination in natural language generation,\" <i>ACM Comput. Surv.</i>, vol. 55, no. 12, 2023.",
        "[3] J. W. Ayers et al., \"Comparing physician and artificial intelligence chatbot responses to patient questions posted to a public social media forum,\" <i>JAMA Intern. Med.</i>, vol. 183, no. 6, pp. 589-596, 2023.",
        "[4] P. Lewis et al., \"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" in <i>Adv. Neural Inf. Process. Syst.</i>, vol. 33, 2020.",
        "[5] G. Xiong, Q. Jin, Z. Lu, and A. Zhang, \"Benchmarking retrieval-augmented generation for medicine,\" in <i>Findings ACL 2024</i>, pp. 6233-6251, 2024.",
        "[6] L. Laranjo et al., \"Conversational agents in healthcare: A systematic review,\" <i>J. Am. Med. Inform. Assoc.</i>, vol. 25, no. 9, pp. 1248-1258, 2018.",
        "[7] A. B. Kocaballi et al., \"The personalization of conversational agents in health care: Systematic review,\" <i>J. Med. Internet Res.</i>, vol. 21, no. 11, e15360, 2019.",
        "[8] R. Ross et al., \"Canadian 24-Hour Movement Guidelines for Adults aged 18-64 years and Adults aged 65 years or older,\" <i>Appl. Physiol. Nutr. Metab.</i>, vol. 45, no. 10 (Suppl. 2), pp. S57-S102, 2020.",
        "[9] F. C. Bull et al., \"World Health Organization 2020 guidelines on physical activity and sedentary behaviour,\" <i>Br. J. Sports Med.</i>, vol. 54, no. 24, pp. 1451-1462, 2020.",
        "[10] CSEP, \"Canadian 24-Hour Movement Guidelines for Adults,\" csepguidelines.ca (accessed Nov. 2026).",
        "[11] <i>Personal Information Protection and Electronic Documents Act</i> (PIPEDA), S.C. 2000, c. 5 (Canada).",
        "[12] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, \"RAGAs: Automated evaluation of retrieval augmented generation,\" in <i>Proc. EACL: System Demonstrations</i>, pp. 150-158, 2024.",
        "[13] Health Canada, \"Canada's Food Guide,\" food-guide.canada.ca (accessed Nov. 2026).",
        "[14] World Health Organization, \"Physical activity\" fact sheet, who.int (accessed Nov. 2026).",
        "[15] A. Grattafiori et al., \"The Llama 3 herd of models,\" arXiv:2407.21783, 2024; Gemma Team, \"Gemma: Open models based on Gemini research and technology,\" arXiv:2403.08295, 2024.",
        "[16] FastAPI (fastapi.tiangolo.com), ChromaDB (trychroma.com), Ollama (ollama.com), LangChain (langchain.com): software documentation, accessed Nov. 2026."]
s += [P(r, ref) for r in refs]

doc = SimpleDocTemplate("docs/P3_CodeHealthCrew.pdf", pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                        topMargin=0.75 * inch, bottomMargin=0.8 * inch, title="P3: Requirements and Design - HealthAssist", author="Code Health Crew")
doc.build(s, onLaterPages=footer)
