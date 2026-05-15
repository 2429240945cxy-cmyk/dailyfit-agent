# Interview Guide

中文简历描述：

> 实现 DailyFit Agent，一个健身饮食垂直 AI Agent：营养数据强制经真实工具查询并带来源归因，长期用户记忆由对话蒸馏后通过 BM25 + 阿里 embedding 混合检索，健康风险由 Guardian 分级拦截，LLM/Judge/Embedding 统一接入阿里百炼 OpenAI-compatible，并配套网页 Demo、JSON audit 和真实数据 benchmark。

English resume bullet:

> Built DailyFit Agent, a vertical fitness and nutrition AI agent with source-attributed real nutrition tools, distilled long-term memory using BM25 plus Aliyun embedding retrieval, a health-safety Guardian, Aliyun Bailian OpenAI-compatible LLM/Judge integration, a usable web UI, JSON audit trails, and real-data benchmarks.

30 秒 pitch：

> DailyFit Agent 是一个日常健身饮食 Agent。重点不是套壳聊天，而是工程边界：营养数字必须来自真实工具并带 source attribution；用户偏好会被蒸馏成长期 memory；健康风险先经过 Guardian；LLM、Judge、Embedding 统一走阿里百炼 OpenAI-compatible；网页可以直接使用；所有 demo、benchmark、audit 都落 JSON，方便复现和排查。

维护流程可以补充说明：项目还包含 GitHub issue-driven 的 self-audit 脚本，用于回归检测、README 数字校验和 no-secret 扫描。
