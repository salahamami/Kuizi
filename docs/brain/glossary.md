# Brain glossary — مسرد مصطلحات الدماغ

The words used in the brain walkthrough (T238), in English and Arabic, with the notebook where each one first appears. French terms are added where Tunisian teachers and students use them.

The Arabic terms follow common usage in Arabic-language education and machine-learning texts; a native-speaker educator should review them before they appear in any student-facing text (T232).

| # | English | العربية | Français | Meaning, in one line | Notebook |
| --- | --- | --- | --- | --- | --- |
| 1 | Knowledge component (KC), concept | مكوّن معرفي، مفهوم | composante de connaissance, notion | A small skill the Bac tests, linked to items | 01 |
| 2 | Prerequisite | مكتسب قبلي، متطلّب سابق | prérequis | A concept that must be known before another | 01 |
| 3 | Concept graph | خريطة المفاهيم | graphe des notions | All concepts and their prerequisite arrows | 01 |
| 4 | Directed acyclic graph (DAG) | بيان موجّه غير دوري | graphe orienté acyclique | Arrows with a direction and no cycle | 01 |
| 5 | Topological order | ترتيب طوبولوجي | ordre topologique | An order where each concept follows its prerequisites | 01 |
| 6 | Mastery | التمكّن | maîtrise | The chance of answering a typical item of a concept correctly | 01 |
| 7 | Item | تمرين، بند | item, exercice | One question shown to a student | 02 |
| 8 | Interaction, event | تفاعل، حدث | interaction, événement | One answer with its details (time, hints…) | 02 |
| 9 | Sequence | متتالية، تسلسل | séquence | A student's interactions in order | 02 |
| 10 | Learning curve | منحنى التعلّم | courbe d'apprentissage | Success rate by practice opportunity | 02 |
| 11 | Elapsed time | الزمن المستغرق | temps de réponse | How long the answer took | 02 |
| 12 | Lag time | الفاصل الزمني | temps écoulé depuis la dernière réponse | Time since the previous answer | 02 |
| 13 | Forgetting | النسيان | oubli | Mastery dropping after a long break | 02 |
| 14 | Synthetic data, simulator | بيانات اصطناعية، محاكي | données synthétiques, simulateur | Generated students whose true knowledge is known | 02 |
| 15 | Padding, mask | حشو، قناع | remplissage, masque | Empty slots in a window, and the marker of real ones | 02 |
| 16 | Item Response Theory (IRT) | نظرية الاستجابة للمفردة | théorie de la réponse à l'item | Ability vs difficulty through a logistic curve | 03 |
| 17 | Ability (θ) | القدرة | aptitude | One number for a student's level in IRT | 03 |
| 18 | Difficulty (b) | الصعوبة | difficulté | One number for an item's level in IRT | 03 |
| 19 | Discrimination (a) | قدرة التمييز | discrimination | How sharply an item separates weak from strong students | 03 |
| 20 | Logistic function, sigmoid | الدالة اللوجستية، السيغمويد | fonction logistique, sigmoïde | Turns any number into a probability between 0 and 1 | 03 |
| 21 | Cold start | البداية الباردة | démarrage à froid | Estimating a new student with no history | 03 |
| 22 | Placement test | اختبار تحديد المستوى | test de positionnement | The 12 first questions that estimate a new student | 03 |
| 23 | Fisher information | معلومات فيشر | information de Fisher | How much an item's answer would reveal right now | 03 |
| 24 | Prior, posterior | التوزيع القبلي، التوزيع البعدي | a priori, a posteriori | Belief before and after seeing the evidence | 03 |
| 25 | Knowledge tracing | تتبّع المعرفة | traçage des connaissances | Following what a student knows over time | 04 |
| 26 | Bayesian Knowledge Tracing (BKT) | تتبّع المعرفة البايزي | traçage bayésien des connaissances | A hidden known / not-known switch per concept | 04 |
| 27 | Guess, slip | التخمين، السهو | devinette, inattention | Right by luck; wrong despite knowing | 04 |
| 28 | Bayes' rule | قاعدة بايز | règle de Bayes | How to update a belief after new evidence | 04 |
| 29 | Loss | دالة الخسارة | fonction de perte | How badly a model predicts; training makes it smaller | 04 |
| 30 | Gradient descent | الانحدار التدرّجي | descente de gradient | Adjusting numbers step by step to reduce the loss | 04 |
| 31 | Neural network | شبكة عصبية | réseau de neurones | A model made of layers of learned numbers | 05 |
| 32 | LSTM, hidden state | ذاكرة طويلة قصيرة المدى، الحالة المخفية | LSTM, état caché | A network that keeps a memory while reading a sequence | 05 |
| 33 | Deep Knowledge Tracing (DKT) | تتبّع المعرفة العميق | traçage profond des connaissances | An LSTM that predicts success on every concept | 05 |
| 34 | Attention | آلية الانتباه | mécanisme d'attention | A weighted look at every past answer | 06 |
| 35 | Query, key, value | الاستعلام، المفتاح، القيمة | requête, clé, valeur | What I look for; what each item is about; what it contains | 06 |
| 36 | Softmax | دالة softmax | fonction softmax | Turns scores into positive weights that add up to 1 | 06 |
| 37 | Causal mask | القناع السببي | masque causal | Forbids looking at future answers | 06 |
| 38 | Attention head | رأس انتباه | tête d'attention | One of several parallel ways of looking at the history | 06 |
| 39 | Transformer | المحوِّل | transformeur | A network built from attention layers | 07 |
| 40 | Embedding | التضمين | plongement, embedding | A learned vector of numbers that represents an item, concept or answer | 07 |
| 41 | Encoder, decoder | المُرمِّز، مُفكِّك الترميز | encodeur, décodeur | SAINT+'s two halves: questions, and answers with time | 07 |
| 42 | Cross-attention | الانتباه المتقاطع | attention croisée | The decoder looking at the encoder | 07 |
| 43 | SAINT+ | SAINT+ | SAINT+ | The transformer Kuizi's brain is built on | 07 |
| 44 | Epoch | حقبة تدريب | époque | One pass over all training data | 07 |
| 45 | Overfitting | فرط التخصيص | surapprentissage | Learning the training students by heart instead of general patterns | 07 |
| 46 | Train / test split by student | تقسيم التدريب والاختبار حسب التلميذ | séparation entraînement / test par élève | Testing only on students the model has never seen | 08 |
| 47 | Data leakage | تسرّب البيانات | fuite de données | Test information sneaking into training and flattering the model | 08 |
| 48 | AUC (area under the ROC curve) | المساحة تحت منحنى ROC | aire sous la courbe ROC | Chance that a right answer gets a higher score than a wrong one | 08 |
| 49 | Calibration, ECE | المعايرة، خطأ المعايرة المتوقّع | calibration, erreur de calibration | Whether "70 %" really means right 70 % of the time | 08 |
| 50 | Champion / challenger | النموذج البطل / النموذج المنافس | champion / challenger | The current model and the new one that must beat it | 08 |
| 51 | Slice | شريحة | sous-groupe | A group of students checked separately (for example accommodations) | 08 |
| 52 | Routing | التوجيه | routage, orientation | Choosing the next item or remediation | 09 |
| 53 | Remediation | المعالجة، الدعم العلاجي | remédiation | A short activity on a weak prerequisite | 09 |
| 54 | Explanation | التفسير | explication | Which past answers drove an estimate | 09 |
| 55 | Fairness | الإنصاف | équité | No group of students treated worse for reasons unrelated to knowledge | 10 |
| 56 | Accommodation, time multiplier | التيسيرات، معامل الوقت الإضافي | aménagement, tiers-temps | Official extra time (×1.33, ×1.5) or assistive tools | 10 |
| 57 | Assistive mode (screen reader) | الوضع المساعد (قارئ الشاشة) | mode assistif (lecteur d'écran) | Using tools that read the screen aloud | 10 |
