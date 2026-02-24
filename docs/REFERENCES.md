# Romulus — Research References

> The science behind the wolf.

Romulus isn't just a metaphor — every subsystem is grounded in real research from neuroscience, immunology, cognitive science, and machine learning. This document cites the 30 papers and books that inform the architecture.

---

## Table of Contents

1. [Episodic vs Semantic Memory](#1-episodic-vs-semantic-memory)
2. [Memory Consolidation During Sleep](#2-memory-consolidation-during-sleep)
3. [Artificial Immune Systems](#3-artificial-immune-systems)
4. [Experience Replay](#4-experience-replay)
5. [Cognitive Architectures](#5-cognitive-architectures)
6. [Tool-Using & Reasoning Agents](#6-tool-using--reasoning-agents)
7. [Confidence Calibration](#7-confidence-calibration)
8. [Evolutionary Computation](#8-evolutionary-computation)
9. [Self-Improving AI Systems](#9-self-improving-ai-systems)
10. [AI Safety & Alignment](#10-ai-safety--alignment)
11. [Local-First Software](#11-local-first-software)
12. [Retrieval-Augmented Generation](#12-retrieval-augmented-generation)

---

## 1. Episodic vs Semantic Memory

*Romulus subsystem: **The Chronicle** — episodic traces (individual experiences) and semantic rules (distilled knowledge)*

**[1]** Tulving, E. (1972). "Episodic and semantic memory." In E. Tulving & W. Donaldson (Eds.), *Organization of Memory*, pp. 381–402. New York: Academic Press.

> The foundational chapter that first proposed the distinction between episodic memory (personal experiences bound to time and place) and semantic memory (general world knowledge). Romulus's architecture directly mirrors this: every task creates an episodic trace, and the Dream Engine distills traces into semantic rules.

**[2]** Tulving, E. (1983). *Elements of Episodic Memory*. Oxford: Clarendon Press.

> The comprehensive elaboration of episodic memory theory. Provides the theoretical basis for treating agent experiences as time-stamped, context-rich episodes that can be replayed and consolidated.

---

## 2. Memory Consolidation During Sleep

*Romulus subsystem: **The Dream Engine** — nightly replay, rule extraction, memory pruning*

**[3]** Diekelmann, S. & Born, J. (2010). "The memory function of sleep." *Nature Reviews Neuroscience*, 11, 114–126. DOI: [10.1038/nrn2762](https://doi.org/10.1038/nrn2762)

> The definitive review of how sleep transforms labile short-term memories into stable long-term representations. Directly inspires the Dream Engine's consolidation phase — replaying episodes and extracting durable rules.

**[4]** Wilson, M. A. & McNaughton, B. L. (1994). "Reactivation of hippocampal ensemble memories during sleep." *Science*, 265(5172), 676–679.

> First demonstration that hippocampal place cells replay waking experiences during slow-wave sleep. This is the direct neuroscience inspiration for the Dream Engine's replay stage, where past episodes are re-processed offline to extract patterns.

**[5]** McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). "Why there are complementary learning systems in the hippocampus and neocortex." *Psychological Review*, 102(3), 419–457. DOI: [10.1037/0033-295X.102.3.419](https://doi.org/10.1037/0033-295X.102.3.419)

> The Complementary Learning Systems (CLS) theory: the brain uses a fast-learning hippocampal system and a slow-learning neocortical system. Romulus mirrors this exactly — episodic traces are fast/specific (hippocampus), semantic rules are slow/general (neocortex), and the Dream Engine mediates consolidation between them.

---

## 3. Artificial Immune Systems

*Romulus subsystem: **The Vigil** — innate pattern matching + adaptive learned defense*

**[6]** Dasgupta, D. (Ed.) (1999). *Artificial Immune Systems and Their Applications*. Berlin: Springer-Verlag.

> The foundational edited volume establishing Artificial Immune Systems (AIS) as a field in computer science. Provides the conceptual framework for the Vigil's two-layered architecture: fast innate responses and slower adaptive learning.

**[7]** de Castro, L. N. & Timmis, J. (2002). *Artificial Immune Systems: A New Computational Intelligence Approach*. Berlin: Springer.

> The comprehensive AIS textbook covering clonal selection, negative selection, danger theory, and immune network models. Provides design patterns for adaptive defense mechanisms like the Vigil's memory cells.

**[8]** Forrest, S., Perelson, A. S., Allen, L., & Cherukuri, R. (1994). "Self-nonself discrimination in a computer." In *Proceedings of the 1994 IEEE Symposium on Research in Security and Privacy*, pp. 202–212. IEEE.

> Introduced the negative selection algorithm inspired by T-cell maturation, where detectors identify "non-self" patterns. Maps to how the Vigil's innate layer identifies dangerous behaviors through pattern matching without needing to learn from incidents.

**[9]** Matzinger, P. (2002). "The Danger Model: A Renewed Sense of Self." *Science*, 296(5566), 301–305. DOI: [10.1126/science.1071059](https://doi.org/10.1126/science.1071059)

> Danger theory: the immune system responds to damage signals rather than foreign-vs-self distinctions. Reframes the Vigil's approach — detecting "danger signals" (destructive patterns, scope violations) rather than just classifying actions as known-good or known-bad.

---

## 4. Experience Replay

*Romulus subsystem: **The Dream Engine** — episode replay for offline learning*

**[10]** Lin, L. J. (1992). "Self-improving reactive agents based on reinforcement learning, planning and teaching." *Machine Learning*, 8, 293–321. DOI: [10.1007/BF00992699](https://doi.org/10.1007/BF00992699)

> The original paper introducing experience replay in reinforcement learning. The Dream Engine's replay of past episodes for learning is a direct analogue — storing experiences and re-processing them offline.

**[11]** Mnih, V., Kavukcuoglu, K., Silver, D., et al. (2015). "Human-level control through deep reinforcement learning." *Nature*, 518(7540), 529–533. DOI: [10.1038/nature14236](https://doi.org/10.1038/nature14236)

> The landmark DQN paper demonstrating experience replay at scale. Validates the principle that replaying stored experiences dramatically improves learning efficiency — the same principle underlying the Dream Engine.

**[12]** Schaul, T., Quan, J., Antonoglou, I., & Silver, D. (2016). "Prioritized Experience Replay." In *ICLR*. arXiv: [1511.05952](https://arxiv.org/abs/1511.05952)

> Introduces prioritized replay where more surprising or informative experiences are replayed more frequently. A future enhancement for the Dream Engine — weighting episodes by learning value.

**[13]** Levine, S., Kumar, A., Tucker, G., & Fu, J. (2020). "Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems." arXiv: [2005.01643](https://arxiv.org/abs/2005.01643)

> Survey of offline RL (learning from fixed datasets without online interaction). Conceptually, this is what the Dream Engine does — learning from stored experience traces without executing new actions.

**[14]** Tadros, T., Krishnan, G. P., Ramyaa, R., & Bazhenov, M. (2022). "Sleep-like unsupervised replay reduces catastrophic forgetting in artificial neural networks." *Nature Communications*, 13, 7742. DOI: [10.1038/s41467-022-34938-7](https://doi.org/10.1038/s41467-022-34938-7)

> Directly bridges neuroscience sleep replay and machine learning, showing that implementing sleep-like replay phases prevents catastrophic forgetting. Validates the Dream Engine's biological metaphor at the algorithmic level.

---

## 5. Cognitive Architectures

*Romulus subsystem: **Overall architecture** — integrated memory, reasoning, learning, and safety subsystems*

**[15]** Laird, J. E., Newell, A., & Rosenbloom, P. S. (1987). "SOAR: An architecture for general intelligence." *Artificial Intelligence*, 33(1), 1–64.

> SOAR's design of integrated memory, learning, and problem-solving subsystems is a direct precursor to Romulus's multi-subsystem design. Both treat the agent as a unified system, not a pipeline of independent components.

**[16]** Anderson, J. R. & Lebiere, C. (1998). *The Atomic Components of Thought*. Mahwah, NJ: Lawrence Erlbaum Associates.

> Presents the ACT-R cognitive architecture with its distinction between declarative and procedural memory. Parallels Romulus's episodic/semantic memory split and the use of learned rules to guide behavior.

**[17]** Kotseruba, I. & Tsotsos, J. K. (2020). "40 years of cognitive architectures: core cognitive abilities and practical applications." *Artificial Intelligence Review*, 53(1), 17–94. DOI: [10.1007/s10462-018-9646-y](https://doi.org/10.1007/s10462-018-9646-y)

> The most comprehensive modern survey of 84 cognitive architectures. Provides context for where Romulus fits in the landscape of integrated AI systems.

**[18]** Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). "Cognitive Architectures for Language Agents." *Transactions on Machine Learning Research*. arXiv: [2309.02427](https://arxiv.org/abs/2309.02427)

> The CoALA framework for understanding LLM-based agents through cognitive architecture principles — mapping memory, action, and decision-making modules. Precisely the design paradigm Romulus employs.

---

## 6. Tool-Using & Reasoning Agents

*Romulus subsystem: **Agent Core** — think-act-observe loop with tool execution*

**[19]** Yao, S., Zhao, J., Yu, D., et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models." In *ICLR*. arXiv: [2210.03629](https://arxiv.org/abs/2210.03629)

> Defines the think-act-observe loop that Romulus's agent core uses. Showed that interleaving reasoning traces with actions yields superior performance over either alone.

**[20]** Schick, T., Dwivedi-Yu, J., Dessi, R., et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." arXiv: [2302.04761](https://arxiv.org/abs/2302.04761)

> Demonstrates that LLMs can autonomously learn when and how to call external tools. Central to Romulus's agent core deciding when to invoke `get_time`, `calculate`, or `get_system_info`.

**[21]** Wei, J., Wang, X., Schuurmans, D., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." In *NeurIPS*, 35, 24824–24837. arXiv: [2201.11903](https://arxiv.org/abs/2201.11903)

> Established that prompting LLMs to produce intermediate reasoning steps improves complex task performance. Romulus requires the LLM to produce a `thought` field before deciding on an action.

---

## 7. Confidence Calibration

*Romulus subsystem: **The Arena** — calibration as a fitness metric*

**[22]** Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). "On Calibration of Modern Neural Networks." In *ICML*, PMLR 70. arXiv: [1706.04599](https://arxiv.org/abs/1706.04599)

> The key paper showing modern neural networks are poorly calibrated (overconfident). Directly motivates the Arena's calibration metric — Romulus needs to know when its confidence predictions are trustworthy.

**[23]** Naeini, M. P., Cooper, G. F., & Hauskrecht, M. (2015). "Obtaining Well Calibrated Predictions Using Bayesian Binning into Quantiles." In *AAAI*.

> Practical calibration measurement techniques. Provides the methodological foundation for how the Arena evaluates whether Romulus's confidence levels match real-world outcomes.

---

## 8. Evolutionary Computation

*Romulus subsystem: **The Arena** (fitness scoring), future **Forge** and **Reaper** (agent evolution)*

**[24]** Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*. Ann Arbor: University of Michigan Press. (2nd ed., MIT Press, 1992.)

> The foundational text on genetic algorithms. The Arena's fitness scoring and the planned Forge/Reaper lifecycle draw on Holland's framework of selection pressure driving adaptation.

**[25]** Koza, J. R. (1992). *Genetic Programming: On the Programming of Computers by Means of Natural Selection*. Cambridge, MA: MIT Press.

> Extends evolutionary computation to evolving entire programs. Relevant to Romulus's vision of evolving agent strategies and behaviors through the Forge (spawning variants) and Reaper (retiring the unfit).

**[26]** Stanley, K. O. & Miikkulainen, R. (2002). "Evolving Neural Networks through Augmenting Topologies." *Evolutionary Computation*, 10(2), 99–127.

> The NEAT algorithm for neuroevolution — evolving both structure and weights. Relevant to future Romulus phases where agent architectures themselves could evolve.

---

## 9. Self-Improving AI Systems

*Romulus subsystem: **The Dream Engine** + **Chronicle** — learning from own experience*

**[27]** Shinn, N., Cassano, F., Berman, E., et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." In *NeurIPS*. arXiv: [2303.11366](https://arxiv.org/abs/2303.11366)

> Reflexion agents maintain episodic memory of verbal self-reflections to improve future performance. Almost exactly what Romulus's Dream Engine does — distilling episodes into rules that improve subsequent behavior.

**[28]** Wang, G., Xie, Y., Jiang, Y., et al. (2023). "Voyager: An Open-Ended Embodied Agent with Large Language Models." arXiv: [2305.16291](https://arxiv.org/abs/2305.16291)

> Voyager accumulates a growing library of reusable skills from experience in Minecraft. Parallels how Romulus accumulates semantic rules from episodic experience. Both are lifelong learning agents that improve through self-directed exploration.

---

## 10. AI Safety & Alignment

*Romulus subsystem: **The Vigil** — action gating, constraint enforcement*

**[29]** Bai, Y., Kadavath, S., Kundu, S., et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." arXiv: [2212.08073](https://arxiv.org/abs/2212.08073)

> Constitutional AI uses a set of principles to guide AI behavior. The Vigil operates on the same principle — encoding safety norms (innate rules) that the agent must follow, plus adaptive learning from violations.

**[30]** Amodei, D., Olah, C., Steinhardt, J., et al. (2016). "Concrete Problems in AI Safety." arXiv: [1606.06565](https://arxiv.org/abs/1606.06565)

> Taxonomizes five concrete safety problems: safe exploration, distributional shift, reward hacking, scalable oversight, and avoiding negative side effects. The Vigil is Romulus's answer to safe exploration and side-effect prevention.

**[31]** Christiano, P. F., Leike, J., Brown, T., et al. (2017). "Deep Reinforcement Learning from Human Preferences." In *NeurIPS*, 30. arXiv: [1706.03741](https://arxiv.org/abs/1706.03741)

> The foundational RLHF paper. The Vigil's adaptive layer, which learns from observed violations, draws on this paradigm of using human preference signals to steer agent behavior.

**[32]** Ouyang, L., Wu, J., Jiang, X., et al. (2022). "Training language models to follow instructions with human feedback." In *NeurIPS*, 35. arXiv: [2203.02155](https://arxiv.org/abs/2203.02155)

> The InstructGPT paper — RLHF at scale for aligning language models with human intent. Provides the practical blueprint for preference-aligned behavior that Romulus maintains through its soul spec and Vigil constraints.

---

## 11. Local-First Software

*Romulus design principle: all data stays on device, no cloud dependency*

**[33]** Kleppmann, M., Wiggins, A., van Hardenberg, P., & McGranaghan, M. (2019). "Local-first software: you own your data, in spite of the cloud." In *Proceedings of the 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software (Onward!)*, pp. 154–178. DOI: [10.1145/3359591.3359737](https://doi.org/10.1145/3359591.3359737)

> The manifesto for local-first software design. Romulus's architecture — running entirely on the user's machine with SQLite storage and local LLM inference via Ollama — is a direct implementation of these principles.

---

## 12. Retrieval-Augmented Generation

*Romulus subsystem: **Agent Core** — injecting learned rules into LLM prompts*

**[34]** Lewis, P., Perez, E., Piktus, A., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." In *NeurIPS*, 33. arXiv: [2005.11401](https://arxiv.org/abs/2005.11401)

> The paper that coined "RAG." Romulus's injection of learned semantic rules and relevant context into prompts at inference time is functionally a RAG system — where the retrieval corpus is the agent's own accumulated experience.

---

## Citation Map

How Romulus subsystems map to research foundations:

```
┌─────────────────────────────────────────────────────────────────┐
│                     ROMULUS ARCHITECTURE                        │
├────────────────┬────────────────────────────────────────────────┤
│  Subsystem     │  Research Foundations                          │
├────────────────┼────────────────────────────────────────────────┤
│  Chronicle     │  Tulving [1,2], McClelland et al. [5]         │
│  (Memory)      │  Anderson & Lebiere [16]                      │
├────────────────┼────────────────────────────────────────────────┤
│  Dream Engine  │  Diekelmann & Born [3], Wilson & McNaughton [4]│
│  (Sleep)       │  Lin [10], Mnih et al. [11], Tadros et al. [14]│
│                │  Shinn et al. [27], Wang et al. [28]          │
├────────────────┼────────────────────────────────────────────────┤
│  Vigil         │  Forrest et al. [8], Matzinger [9]            │
│  (Immunity)    │  Dasgupta [6], de Castro & Timmis [7]         │
│                │  Bai et al. [29], Amodei et al. [30]          │
├────────────────┼────────────────────────────────────────────────┤
│  Arena         │  Holland [24], Guo et al. [22]                │
│  (Fitness)     │  Naeini et al. [23]                           │
├────────────────┼────────────────────────────────────────────────┤
│  Agent Core    │  Yao et al. [19], Schick et al. [20]          │
│  (Reasoning)   │  Wei et al. [21], Lewis et al. [34]           │
├────────────────┼────────────────────────────────────────────────┤
│  Forge/Reaper  │  Holland [24], Koza [25]                      │
│  (Evolution)   │  Stanley & Miikkulainen [26]                  │
├────────────────┼────────────────────────────────────────────────┤
│  Architecture  │  Laird et al. [15], Kotseruba & Tsotsos [17]  │
│  (Overall)     │  Sumers et al. [18], Kleppmann et al. [33]    │
└────────────────┴────────────────────────────────────────────────┘
```

---

## Summary

| Category | Papers | Span |
|----------|--------|------|
| Cognitive Psychology | 2 | 1972–1983 |
| Neuroscience | 3 | 1994–2022 |
| Immunology & AIS | 4 | 1994–2002 |
| Reinforcement Learning | 5 | 1992–2022 |
| Cognitive Architectures | 4 | 1987–2024 |
| LLM Agents | 3 | 2022–2023 |
| Calibration | 2 | 2015–2017 |
| Evolutionary Computation | 3 | 1975–2002 |
| Self-Improving AI | 2 | 2023 |
| AI Safety | 4 | 2016–2022 |
| Local-First Software | 1 | 2019 |
| RAG | 1 | 2020 |
| **Total** | **34** | **1972–2024** |

---

*Every rule Romulus knows was earned. Every design decision has a citation.*
