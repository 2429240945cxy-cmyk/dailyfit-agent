# Memory Design

User preferences, constraints, goals, and profile facts are distilled into
SQLite rows. Retrieval uses BM25 plus lexical overlap in demo mode. Live mode is
ready for Aliyun `text-embedding-v4` hybrid retrieval.

The single-document BM25 zero-score issue is handled by lexical overlap, so
queries such as `牛肉饮食` hit `用户不吃牛肉`.
